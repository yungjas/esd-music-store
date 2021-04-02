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
error_url = "http://localhost:6003/error"

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

    # invoke error microservice here if order creation is not successful
    code = order_result["code"]
    if code not in range(200, 300):
        error_cat = "Order"
        error_desc = "Order creation failure"

        error_order = {
            "error_category": error_cat,
            "error_desc": error_desc
        }

        print('\n\n-----Invoking error microservice as order fails-----')
        invoke_http(error_url, method="POST", json=error_order)
        print("Order status ({:d}) sent to the error microservice:".format(code), order_result)

    # if order creation successful
    else:    
        # invoke inventory microservice to check if item quantity is sufficient
        # if not then trigger error microservice
        print("\n-----Invoking inventory microservice-----")
        for each_order_item in order["cart_item"]:
            print(each_order_item["item_id"])
            item_info = invoke_http(inventory_url + "/" + each_order_item["item_id"], method="GET", json=each_order_item["item_id"])
            print("item_info:", item_info)

            if item_info["data"]["item_quantity"] == 0:
                print("ItemID " + item_info["data"]["item_id"] + " is out of stock")

            # don't add to total amount if an item has insufficient stock
            else:
                total_amount += (item_info["data"]["item_price"]) * (each_order_item["quantity"])
                
        # invoke payment microservice - charge total amount
        print("\n-----Invoking payment microservice-----")
        payment_result = invoke_http(payment_url, method="POST", json=total_amount)

        # invoke error microservice here if payment transaction is not successful
        code = payment_result["code"]
        if code not in range(200, 300):
            error_cat = "Payment"
            error_desc = "Payment failure"

            error_payment = {
                "error_category": error_cat,
                "error_desc": error_desc
            }

            print('\n\n-----Invoking error microservice as payment fails-----')
            invoke_http(error_url, method="POST", json=error_payment)
            print("Payment status ({:d}) sent to the error microservice:".format(code), payment_result)
        
        # after successful payment, update item quantity in inventory
        else:
            for each_order_item in order["cart_item"]:
                print(each_order_item["item_id"])
                item_info = invoke_http(inventory_url + "/" + each_order_item["item_id"], method="GET", json=each_order_item["item_id"])
                print("item_info:", item_info)

                # update quantity
                item_info["data"]["item_quantity"] = item_info["data"]["item_quantity"] - each_order_item["quantity"]
                print(item_info["data"]["item_quantity"])

                # if after updating quantity, the quantity reaches 0
                if item_info["data"]["item_quantity"] == 0:
                    # update item status
                    item_info["data"]["item_status"] = "Out of Stock"
                    print(item_info)

                invoke_http(inventory_url + "/" + each_order_item["item_id"], method="PUT", json=item_info)
    
    return {
        "code": 201,
        "data":{
            "order_result": order_result,
            "payment_result": payment_result
        }
    }
    

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=6100, debug=True)