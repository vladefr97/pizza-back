import json

from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import InternalServerError

from conf import database
from server.libs.db_handler import MySQLHandler

app = Flask(__name__, static_folder='main/static')
app.config['SECRET_KEY'] = '57451638b20w13cd0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Importing api from modules
from server.api import routes
from server.user import user_routes

# API Blueprints registration
app.register_blueprint(routes.api, url_prefix="/api")
app.register_blueprint(user_routes.user, url_prefix="/user")

# Обработки ошибки 500
@app.errorhandler(InternalServerError)
def handle_500(e):
    return json.dumps({'error': str(e)}), e.code


app.register_error_handler(500, handle_500)
