from flask import Flask, request, jsonify
from flask_cors import CORS

import os

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

order_url = "http://localhost:6001/order"
inventory_url = "http://localhost:6000/inventory"
payment_url = "http://localhost:6002/payment"
error_url = ""

@app.route("/place_order", methods=['POST'])
def place_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order = request.get_json()
            print("\nReceived an order in JSON:", order)

            # do the actual work
            # 1. Send order info {cart items}
            result = processPlaceOrder(order)
            return jsonify(result), 200

        except Exception as e:
            pass  # do nothing.

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processPlaceOrder(order):
    total_amount = 0
    
    # invoke order microservice
    # if item in an order is out of stock, can still go thru the order microservice for logging purposes - if the item has been restocked, staff can follow up on the order of the item
    print("\n-----Invoking order microservice-----")
    order_result = invoke_http(order_url, method="POST", json=order)
    print("order_result:", order_result)

    # invoke error microservice here
    
    # invoke inventory microservice to check if item quantity is sufficient
    # if not then trigger error microservice
    print("\n-----Invoking inventory microservice-----")
    for each_order_item in order["cart_item"]:
        print(each_order_item["item_id"])
        item_info = invoke_http(inventory_url + "/" + each_order_item["item_id"], method="GET", json=each_order_item["item_id"])
        print("item_info:", item_info)

        if item_info["data"]["item_quantity"] == 0:
            print("ItemID " + item_info["data"]["item_id"] + " is out of stock")

        # invoke order microservice and payment microservice if sufficient stock
        else:
            total_amount += (item_info["data"]["item_price"]) * (each_order_item["quantity"])
            # update quantity
            item_info["data"]["item_quantity"] = item_info["data"]["item_quantity"] - each_order_item["quantity"]
            print(item_info["data"]["item_quantity"])
            invoke_http(inventory_url + "/" + each_order_item["item_id"], method="PUT", json=item_info)
    
    # invoke payment microservice - charge total amount
    print("\n-----Invoking payment microservice-----")
    payment_result = invoke_http(payment_url, method="POST", json=total_amount)
    
    return {
        "code": 201,
        "data":{
            "order_result": order_result,
            "payment_result": payment_result
        }
    }

    # invoke error microservice

    # invoke notification microservice
    

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=6100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.