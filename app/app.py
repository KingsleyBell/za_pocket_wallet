import datetime
import hashlib
import json
import os
import urllib

from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo

from auth import requires_auth
from encoder import JSONEncoder


# the all-important app variable:
application = Flask(__name__)


# add mongo url to flask config, so that flask_pymongo can use it to make connection
application.config['MONGO_URI'] = os.environ.get('DB')
mongo = PyMongo(application)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
application.json_encoder = JSONEncoder


@application.route('/')
def home(country='USA', promo=False):
    db_path = os.path.join(application.static_folder, 'catalogue/db.json')
    db = json.loads(open(db_path, 'r').read())
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        colour = request.form.get('colour')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        address1 = request.form.get('address1')
        address2 = request.form.get('address2')
        city = request.form.get('city')
        country = request.form.get('country')
        zip_code = request.form.get('zip-code')
        payment_id = str(datetime.datetime.timestamp(datetime.datetime.now()))

        data = {
            'payment_id': payment_id,
            'quantity': quantity,
            'colour': colour,
            'name': name,
            'surname': surname,
            'email': email,
            'address1': address1,
            'address2': address2,
            'city': city,
            'country': country,
            'zip_code': zip_code,
            'paid': False
        }

        mongo.db.orders.insert_one(data)

        post_data = {
            'merchant_id': 10000100, # non sandbox 11070985,
            'merchant_key': '46f0cd694581a', # non sandbox''22ha4oa68qbxa',
            'return_url': 'https://www.pocketwallet.co.za/order-complete/',
            'cancel_url': 'https://www.pocketwallet.co.za/order-cancelled/',
            'notify_url': 'https://www.pocketwallet.co.za/notify-payment/',
            'name_first': name,
            'name_last': surname,
            'email_address': email,
            'm_payment_id': payment_id,
            'amount': quantity * 150,
            'item_name': f'Pocket Wallet (x {quantity})'
        }

        md5 = hashlib.md5(urllib.parse.urlencode(post_data).encode('utf-8')).hexdigest()
        post_data['signature'] = md5

        return jsonify(post_data)

    else:
        return render_template(
            'index.html',
            links=db,
            promo=promo,
            country=country
        )


@application.route('/US/')
def us():
    return home()


@application.route('/ZA/', methods=['GET', 'POST'])
def za():
    return home(country='ZA')


@application.route('/promo/')
def promo():
    return home(promo=True)


@application.route('/order-cancelled/')
def order_cancelled():
    order_status_message = (
        "Order successfully cancelled."
        "<br><br>"
        "Navigate back to store to continue shopping."
    )
    return render_template(
        'order_status.html',
        order_status_message=order_status_message
    )


@application.route('/order-complete/')
def order_complete():
    order_status_message = (
        "Thank you for your order!"
        "<br><br>"
        "You will receive details via email, "
        "and your package will be shipped within the next 48 hours :)"
    )
    return render_template(
        'order_status.html',
        order_status_message=order_status_message
    )


@application.route('/delete-order/', methods=['POST'])
def delete_order():
    data = request.form

    mongo.db.orders.delete_one(data)

    return jsonify({'ok': True, 'message': 'Order successfully removed'}), 200


@application.route('/notify-payment/', methods=['POST'])
def notify_payment():
    data = request.form.to_dict()

    successful_payment = data['payment_status'] == 'COMPLETE'
    application.logger.error(f"data: {data['payment_status']}. Success: {successful_payment}")

    if successful_payment:
        order_query = {'payment_id': data['m_payment_id']}
        order_update = {"$set": {'paid': True}}
        application.logger.error(f'query: {order_query}. Update: {order_update}')

        mongo.db.orders.update_one(order_query, order_update)

    mongo.db.orderConfirmations.insert_one(data)

    return jsonify({'ok': True, 'message': 'Order success'}), 200


@application.route('/order/', methods=['GET'])
@requires_auth
def order():
    if request.method == 'GET':
        orders = [o for o in mongo.db.orders.find()]
        confirmations = [c for c in mongo.db.orderConfirmations.find()]
        return render_template(
            'orders.html',
            orders=orders,
            confirmations=confirmations
        )


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=800)
