import json
from uuid import uuid4

from flask import request
# Project imports
from werkzeug.security import generate_password_hash, check_password_hash

from conf import database
from server import MySQLHandler, app
from server.user import user

# Initializing MySQL DB Handler
db_handler = MySQLHandler(app=app, db_host=database['host'], db_name=database['name'], db_user=database['user'],
                          db_password=database['password'])


@user.route('/register', methods=['POST'])
def register():
    try:
        # Parsing user data
        user_data = json.loads(request.get_data())

        # Generate password hash
        _hashed_password = generate_password_hash(user_data['password'])

        # Interact with database
        db_handler.connect()
        user_id = db_handler.execute_insert(
            query='insert into user (u_login,u_email,u_telephone,u_password) values(%s,%s,%s,%s)',
            data=[(user_data['login'], user_data['email'], '8888888', _hashed_password)]
        ).data['lastid']
        db_handler.close_connection()

        # Create client token
        rand_token = str(uuid4())
        return json.dumps(
            {'user': {'id': user_id, 'login': user_data['login'], 'email': user_data['email'],
                      "access_token": rand_token}})
    except BaseException as e:
        pass


@user.route('/login', methods=['POST'])
def login():
    try:
        # Parsing user data
        user_data = json.loads(request.get_data())

        db_handler.connect()
        data = db_handler.execute_select(
            query='select distinct * from user where u_login=%s',
            data=[user_data['login']]
        ).data[0]
        _hashed_password = data[4]
        _user_id = data[0]
        _user_login = data[1]
        _user_email = data[2]
        _user_phone = data[3]
        _random_token = str(uuid4())
        if check_password_hash(_hashed_password, user_data['password']):
            return json.dumps(
                {'user': {'id': _user_id, 'login': _user_login, 'email': _user_email,
                          "access_token": _random_token}})
        else:
            return "Access Denied"

    except BaseException as e:
        pass


@user.route('/<user_id>/orders')
def get_order(user_id):
    db_handler.connect()
    user_id = int(user_id)
    request = "select p.p_id,p.p_name , p.p_descr, p.p_price, ohp.product_count,ohp.multiplier,ohp.params, uo.o_date,uo.o_sum,uo.o_currency  from product as p " \
              "inner join order_has_product as ohp on ohp.product_p_id = p.p_id " \
              "inner join user_order as uo on uo.o_id=ohp.order_o_id where uo.o_id=%s"

    user_orders = db_handler.execute_select(query='select * from user_order where o_u_id=%s',
                                            data=[(user_id)]).data
    ret_data = []
    # TODO: елать нормально в for
    index = 0
    for order in user_orders:
        order_data = db_handler.execute_select(query=request, data=[(order[0])]).data
        ret_data.append({'orderItems': [{'product': {'id': product[0], 'name': product[1], 'description': product[2],
                                                     'price': product[3], 'priceMultiplier': product[5],
                                                     'params':json.loads(product[6]),
                                                     'imgName': product[0]},
                                         'count': product[4]}
                                        for product in
                                        order_data],
                         'timestamp': user_orders[0][1],
                         'price': float(user_orders[index][3]),
                         'currency': user_orders[index][4]
                         })
        index += 1
        print(ret_data)

    db_handler.close_connection()
    ret  = json.dumps(ret_data)
    return ret
