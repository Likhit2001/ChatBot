
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db
import session_id

app = FastAPI()


inprogress_order ={

}

# track_order

@app.post("/")
async def handle_request(request : Request):

    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session = session_id.extract_sessions_id(output_contexts[0]['name'])


    if intent == "track_orderID":
        return track_order(parameters)
        # return JSONResponse(content={
        #     "fulfillmentText": f"hehe backend"
        # })
    elif intent == "order_add":
        return add_to_order(parameters,session)

    elif intent == "Order_complete":
        return complete_order(parameters,session)

    elif intent == 'remove_order':
        return remove_item(parameters,session)

# remove item


def remove_item (parameters :dict , session : str):
    print(session)
    if session not in inprogress_order:
        return JSONResponse(content={
            'fulfillmentText' : "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    })

    food_items = parameters["food_items"]
    current_order = inprogress_order[session]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = session_id.get_string(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })





# finally saving the order
def complete_order (parameters : dict , session_ids : str):
    if session_ids not in inprogress_order:
        fulfillment_text = "having trouble placing your order you need to place your order again"
    else:

        order = inprogress_order[session_ids]
        order_ids = save_to_db(order)
        order_total = db.get_total_order_price(order_ids)
        fulfillment_text = f"the order has been placed {order_ids}" \
                           f"Your order total is {order_total} which you can pay at the time of delivery!"


    del inprogress_order[session_ids]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



# // first time adding to the orders
def add_to_order(parameters : dict , session : str):


    food_items = parameters["food_items"]
    number = parameters["number"]

    if(len(food_items) != len(number)):
        fulfillment_text = "sorry specify food items and quantity crctly"
    else:
        new_food_list = dict(zip(food_items,number))

        if session in inprogress_order:

            current_food_list = inprogress_order[session]
            current_food_list.update(new_food_list)
            inprogress_order[session] = current_food_list

        else:
            print(session)
            inprogress_order[session] = new_food_list

        order_str = session_id.get_string(inprogress_order[session])

        fulfillment_text = f"So far  you have {order_str}, {session} Do you like to add anything else"


    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



# use to track the order
def track_order(parameters : dict):
    order_id = int(parameters['number'])
    order_status = db.get_order_status(order_id)
    if order_status:
        out = f" the order status for order id: {order_id} is : {order_status}"
    else:
        out = f" the order not found"

    return JSONResponse(content={
        "fulfillmentText": out
    })


# // to save the data in the db
def save_to_db(order: dict):
    next_order_id = db.orderid_max()
    for food_item, number in order.items():
        db.insert_order_item(
            food_item,
            number,
            next_order_id
        )

    db.insert_order_tracking(next_order_id,"in progress")

    return next_order_id




