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
    # invoke order microservice
    print("\n-----Invoking order microservice-----")
    order_result = invoke_http(order_url, method="POST", json=order)
    print("order_result:", order_result)

    # invoke inventory microservice
    # check if item quantity is sufficient
    # if not then trigger error microservice
    # print("\n-----Invoking inventory microservice-----")
    # for each_order_item in order_result["data"]["order_item"]:
    #     invoke_http(inventory_URL, method="GET", json=each_order_item["quantity"])

    # invoke payment microservice
    print("\n-----Invoking payment microservice-----")
    # for each order item, go through the stripe payment
    for each_order_item in order_result["data"]["order_item"]:
        print(each_order_item["amount"])
        invoke_http(payment_url, method="POST", json=each_order_item["amount"])
    
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