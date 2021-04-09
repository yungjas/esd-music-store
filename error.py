import sys
import os
import json
import amqp_setup
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3308/error'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

monitor_binding_key ='*.error'

class Error(db.Model):
    __tablename__ = 'error'
    error_id = db.Column(db.Integer, primary_key=True)
    error_category = db.Column(db.String(64), nullable=False)
    error_desc = db.Column(db.String(255), nullable=False)

    def json(self):
        return {"error_id": self.error_id, "error_category": self.error_category, "error_desc": self.error_desc}

#@app.route("/error", methods=['POST'])
def receive_error():
    amqp_setup.check_setup()
    queue_name = "Error_Music"
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming()

def callback(channel, method, properties, body):
    print("Received error")
    process_error(body)
    print()

def process_error(error_msg):
    try:
        error = json.loads(error_msg)
        error_category = error["error_category"]
        error_desc = error["error_desc"]
        error = Error(error_category=error_category, error_desc=error_desc)
        
        db.session.add(error)
        db.session.commit()
    except Exception as e:
        pass

if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitor_binding_key, amqp_setup.exchangename))
    #app.run(port=7003, debug=True)
    receive_error()