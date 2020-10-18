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
    order_data = json.loads(request.get_data())
    db_handler.connect()
    print('connected')
    db_handler.close_connection()

