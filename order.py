import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

app = Flask(__name__)
# need to change this later
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3308/order_music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_address = db.Column(db.String(100), nullable=False)
    telegram_id = db.Column(db.String(32), nullable=True)
    customer_contact = db.Column(db.String(10), nullable=False)
    
    # timestamp
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified = db.Column(db.DateTime, nullable=False,
                         default=datetime.now, onupdate=datetime.now)
    
    def json(self):
        dto = {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'telegram_id': self.telegram_id,
            'customer_contact': self.customer_contact,
            'created': self.created,
            'modified': self.modified
        }

        dto['order_item'] = []
        for oi in self.order_item:
            dto['order_item'].append(oi.json())

        return dto


class Order_Item(db.Model):
    __tablename__ = 'order_item'
     
    order_item_id = db.Column(db.Integer, primary_key=True)
    
    order_id = db.Column(db.ForeignKey(
        'order.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    
    item_id = db.Column(db.String(13), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    
    #amount = db.Column(db.Float(precision=2), nullable=False)

    order = db.relationship(
        'Order', primaryjoin='Order_Item.order_id == Order.order_id', backref='order_item')

    def json(self):
        return {'order_item_id': self.order_item_id, 'order_id': self.order_id, 'item_id': self.item_id, 'quantity': self.quantity}

@app.route("/order")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

@app.route("/order/<string:order_id>")
def find_by_order_id(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "order_id": order_id
            },
            "message": "Order not found."
        }
    ), 404

@app.route("/order", methods=['POST'])
def create_order():
    customer_id = request.json.get('customer_id', None)
    customer_name = request.json.get('customer_name', None)
    customer_address = request.json.get('customer_address', None)
    customer_contact = request.json.get('customer_contact', None)
    telegram_id = request.json.get('telegram_id', None)
    order = Order(customer_id=customer_id, customer_name=customer_name, customer_address=customer_address, customer_contact=customer_contact, telegram_id=telegram_id)
    print(order)

    cart_item = request.json.get('cart_item')
    for each_item in cart_item:
        order.order_item.append(Order_Item(
            item_id=each_item['item_id'], quantity=each_item['quantity']))

    try:
        db.session.add(order)
        db.session.commit()
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
            "data": order.json()
        }
    ), 201

# specifies the port to run this microservice on
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(port=6001, debug=True)
