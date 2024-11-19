"""
Sub módulo de api. Aca estaria la definición de la API y la URL
"""
from flask import Blueprint, Flask, render_template
from flask_restx import Api
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import config

## IDEA: HACEMOS ESTO COMO FACTORY METHOD
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/html'), static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/static'))

app.config.from_object(config.Config)
app.secret_key=config.Config.user_secret
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
if not database_exists(engine.url):
    create_database(engine.url)

api_blueprint = Blueprint('api', __name__)
views = Blueprint("views",__name__)
#api_v1 = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_blueprint,
    version="1.0",
    title="MerendAR",
    description="Merendate esta",
    doc='/docs'
)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(views)
from .App import ns as ns_api
api.add_namespace(ns_api)

from .models import db, ConfirmedUser, PotentialUser, ProfilePicture, Folders, MenuItems, SavedItems, Reviews, Establishments
db.init_app(app)
with app.app_context():
    db.create_all()  

