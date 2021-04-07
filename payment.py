#--------------IDEA----------------- 
# create a database for payment, will have paymentid, amount
# post to payment microservice, then call stripe (send payment id and amount to stripe)

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from os import environ

import stripe

import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3308/payment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Stripe config
stripe_keys = {
#   'secret_key': os.environ['STRIPE_SECRET_KEY'],
#   'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']

  'publishable_key': '',
  'secret_key': ''
}

stripe.api_key = stripe_keys['secret_key']

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float(precision=2), nullable=False)

    # def __init__(self, payment_id, amount):
    #     self.payment_id = payment_id
    #     self.amount = amount
    
    def json(self):
        return {'payment_id': self.payment_id, 'amount': self.amount}

@app.route("/payment/<string:payment_id>")
def get_payment(payment_id):
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if payment:
        return jsonify(
            {
                "code": 200,
                "data": payment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Transaction not found."
        }
    ), 404

@app.route("/payment", methods=['POST'])
def create_payment():
    amount = request.get_json()
    #data = request.get_json()
    payment = Payment(amount=amount)
    # stripe only accepts amounts in cents
    amount_in_cents = math.ceil(amount * 100)

    try:
        db.session.add(payment)
        db.session.commit()

        # Stripe charge
        # thinking of adding billing address, type of card i.e. visa, mastercard etc
        resp = stripe.Charge.create( 
            amount = amount_in_cents,
            source = "tok_visa",
            currency = "sgd",
            description = "Payment transaction successful"
        )
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": payment.json()
        }
    ), 201

# specifies the port to run this microservice on
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage payment ...")
    app.run(host='0.0.0.0', port=7002, debug=True)