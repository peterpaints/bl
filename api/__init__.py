from flask import Flask, Blueprint
from instance.config import app_config
from api.restplus import api
from api.auth.views import ns as auth_namespace
from api.bucketlists.endpoints.bucketlists import ns as bucketlists_namespace
from api.bucketlists.endpoints.items import ns as items_namespace
from models.models import db
from flask_cors import CORS


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
    api.init_app(api_blueprint)
    api.add_namespace(bucketlists_namespace)
    api.add_namespace(auth_namespace)
    api.add_namespace(items_namespace)
    app.register_blueprint(api_blueprint)

    db.init_app(app)
    return app
