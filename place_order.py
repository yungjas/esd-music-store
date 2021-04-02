from flask import Flask, request, jsonify
from flask_cors import CORS

import os

import requests
from invokes import invoke_http

import amqp_setup
import pika

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
        
        # if possible consume messages from amqp and save to database
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error", 
            body=error_desc, properties=pika.BasicProperties(delivery_mode = 2))

        invoke_http(error_url, method="POST", json=error_order)
        
        #print("Order status ({:d}) sent to the error microservice:".format(code), order_result)

        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), order_result)

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
                # make sure status is set to out of stock
                if item_info["data"]["item_status"] != "Out of Stock":
                    item_info["data"]["item_status"] = "Out of Stock"

                    # update inventory database
                    invoke_http(inventory_url + "/" + item_info["data"]["item_id"], method="PUT", json=item_info)

                # invoke error microservice
                error_insufficient_stock = {
                    "error_category": "Insufficient stock",
                    "error_desc": item_info["data"]["item_name"] + " is currently out of stock"
                }
                
                print('\n\n-----Invoking error microservice as there is insufficient stock-----')
                invoke_http(error_url, method="POST", json=error_insufficient_stock)

            # when order quantity is more than item quantity
            elif each_order_item["quantity"] > item_info["data"]["item_quantity"]:
                print('\n\n-----Invoking error microservice as order quantity is more than item quantity-----')
                invoke_http(error_url, method="POST", json=error_insufficient_stock)

            # don't add to total amount if an item has insufficient stock
            else:
                total_amount += (item_info["data"]["item_price"]) * (each_order_item["quantity"])
        
        if total_amount > 0:
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

                # only update quantity when quantity > 0
                if item_info["data"]["item_quantity"] > 0:
                    item_info["data"]["item_quantity"] = item_info["data"]["item_quantity"] - each_order_item["quantity"]
                    print(item_info["data"]["item_quantity"])

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