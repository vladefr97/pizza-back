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
