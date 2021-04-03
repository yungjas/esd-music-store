import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3308/inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    item_id = db.Column(db.String(64), primary_key=True)
    item_name = db.Column(db.String(64), nullable=False)
    artist = db.Column(db.String(64), nullable=True)
    item_price = db.Column(db.Float(precision=2), nullable=False)
    item_category = db.Column(db.String(64), nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)
    item_status = db.Column(db.String(64), nullable=False)

    def __init__(self, item_id, item_name, artist, item_price, item_category, item_quantity, item_status):
        self.item_id = item_id
        self.item_name = item_name
        self.artist = artist
        self.item_price = item_price
        self.item_category = item_category
        self.item_quantity = item_quantity
        self.item_status = item_status
    
    def json(self):
         return {"item_id": self.item_id, "item_name": self.item_name, "artist": self.artist, "item_price": self.item_price, "item_category": self.item_category, "item_quantity": self.item_quantity, "item_status": self.item_status}

@app.route("/inventory")
def get_all():
    inventorylist = Inventory.query.all()
    if len(inventorylist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "inventories": [inventory.json() for inventory in inventorylist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no inventories."
        }
    ), 404

@app.route("/inventory/<string:item_id>")
def find_by_item_id(item_id):
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    if inventory:
        return jsonify(
            {
                "code": 200,
                "data": inventory.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Item not found."
        }
    ), 404

@app.route("/inventory/<string:item_id>", methods=['POST'])
def create_item(item_id):
    if (Inventory.query.filter_by(item_id=item_id).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "item_id": item_id
                },
                "message": "Item already exists."
            }
        ), 400

    data = request.get_json()
    inventory = Inventory(item_id, **data)

    try:
        db.session.add(inventory)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "item_id": item_id
                },
                "message": "An error occurred creating the item."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": inventory.json()
        }
    ), 201

@app.route("/inventory/<string:item_id>", methods=['PUT'])
def update_item(item_id):
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    
    if inventory:
        json_data = request.get_json()
        data = json_data["data"]
        print(data)
        
        if data['item_name']:
            inventory.item_name = data['item_name']
        if data['artist']:
            inventory.artist = data['artist']
        if data['item_price']:
            inventory.item_price = data['item_price']
        if data['item_quantity'] or data['item_quantity'] == 0:
            inventory.item_quantity = data['item_quantity']
        if data['item_category']:
            inventory.item_category = data['item_category']
        if data['item_status']:
            inventory.item_status = data['item_status']

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": inventory.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "item_id": item_id
            },
            "message": "Item not found."
        }
    ), 404


@app.route("/inventory/<string:item_id>", methods=['DELETE'])
def delete_item(item_id):
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    if inventory:
        db.session.delete(inventory)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "item_id": item_id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "item_id": item_id
            },
            "message": "Item not found."
        }
    ), 404

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": inventory ...")
    app.run(port=7000, debug=True)