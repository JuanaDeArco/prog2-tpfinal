"""
Sub módulo de api. Aca estaria la definición de la API y la URL
"""
from flask import Blueprint, Flask
from flask_restx import Api
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import config
import sys
from logging.config import dictConfig
from .populate_db import populate_table_from_csv

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/html'), static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/static'))

app.config.from_object(config.Config)
if os.environ.get('TESTING') == 'True':
    URI='sqlite:///test.db'
    app.config.from_object(config.ConfigTest)
else:
    URI=app.config["SQLALCHEMY_DATABASE_URI"]

app.secret_key=config.Config.user_secret
try:
    engine = create_engine(URI)
except ValueError:
    app.logger.critical(f">>>>>>>>>>{os.environ.get('TESTING')}")
if not database_exists(engine.url):
    create_database(engine.url)

api_blueprint = Blueprint('api', __name__)
views = Blueprint("views",__name__)
#api_v1 = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_blueprint,
    version="1.0",
    title="MerendAR",
    description="Una Api con Bizcochitos. Esto es EXPERIMENTAL",
    doc='/docs'
)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(views)
from .App import ns as ns_api
api.add_namespace(ns_api)

from .models import db, ConfirmedUser, PotentialUser, ProfilePicture, Folders, MenuItems, SavedItems, Reviews, Establishments, Promotion, Followers
db.init_app(app)

with app.app_context():
    db.create_all()
    static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/static')
    #csv_file_path = os.path.join(static_folder_path, 'data/ARCHIVO.csv')
    #app.logger.debug('Meto datos mock de establishments')
    #populate_table_from_csv(csv_file_path,Establishments,db.session)

with open("app/assets/static/arte.txt") as f:
    print(f.read(), flush=True)
