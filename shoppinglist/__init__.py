import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from shoppinglist.config import configurations

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=True
    )

    return app
