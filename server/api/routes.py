import json

from flask import request

from server.api import api
from server.libs import db_handler
from conf import database
from server import MySQLHandler, app

# Initializing MySQL DB Handler
db_handler = MySQLHandler(app=app, db_host=database['host'], db_name=database['name'], db_user=database['user'],
                          db_password=database['password'])


@api.route('/order', methods=['POST'])
def make_order():
    try:
        order = json.loads(request.get_data())
        service_info = order['serviceInformation']
        order_info = order['orderInformation']
        db_handler.connect()
        order_id = db_handler.execute_insert(
            query='insert into user_order (o_date, o_u_id, o_address,o_sum,o_currency) values (%s,%s,%s,%s,%s)',
            data=[(order['timestamp'],
                   order_info['userId'],
                   order_info['totalSum'],
                   order_info['currency'],
                   f"{service_info['address']} {service_info['apartment']} "
                   f"{service_info['floor']}")]).data['lastid']

        for item in order['items']:
            db_handler.execute_insert(
                query='insert into order_has_product (order_o_id,product_p_id,product_count,multiplier,params) values(%s,%s,%s,%s,%s)',
                data=[(order_id, item['product']['id'], item['count'],
                       item['product']['priceMultiplier'],
                       json.dumps(item['product']['params'])
                       )])

        db_handler.close_connection()
        return json.dumps({'status': "OK"})

    except BaseException as e:
        e = str(e)
        print(e)


@api.route('/all-products', methods=['GET'])
def all_products():
    db_handler.connect()
    db_products = db_handler.execute_select(query='select * from product').data
    db_handler.close_connection()
    products = [{'id': product[0], 'name': product[1], 'description': product[2], 'basePrice': product[3],
                 'imgName': product[0]}
                for product in db_products]
    return json.dumps(products)
