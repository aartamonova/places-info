from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)
bootstrap = Bootstrap(app)

from places_info.routes import index_routes, errors_routes, auth_routes, statistic_routes, tags_routes, places_routes

# Migration
from places_info import places_info_model
