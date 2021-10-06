from flask import Flask
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from user import api

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:new_password@localhost:5432/p_user"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(flask_app)
api.init_app(flask_app)

db.create_all()
flask_app.run(debug=True)