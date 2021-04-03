import sys
import os
import json
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

class Error(db.Model):
    __tablename__ = 'error'
    error_id = db.Column(db.Integer, primary_key=True)
    error_category = db.Column(db.String(64), nullable=False)
    error_desc = db.Column(db.String(255), nullable=False)

    def json(self):
        return {"error_id": self.error_id, "error_category": self.error_category, "error_desc": self.error_desc}

@app.route("/error", methods=['POST'])
def create_error():
    error_category = request.json.get("error_category", None)
    error_desc = request.json.get("error_desc", None)
    error = Error(error_category=error_category, error_desc=error_desc)
    print(error)

    try:
        db.session.add(error)
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
            "data": error.json()
        }
    ), 201

if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) + ": processing errors ...")
    app.run(port=7003, debug=True)