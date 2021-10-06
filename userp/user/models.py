import datetime
import json
import uuid

import glog as log
import jwt
from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from constants import db


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(254), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String())
    password = db.Column(db.String(100))

    def __init__(self, user_data=None):
        if not user_data:
            user_data = {}
        self.email = user_data.get("email")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.phone_number = user_data.get("phone_number")
        if user_data.get("password"):
            self.password = Bcrypt().generate_password_hash(user_data.get("password")).decode()

    def to_response_dict(self):
        """
        Helps json-ify the user object for sending to FE.
        """
        resp_dict = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number
        }
        return resp_dict

    @staticmethod
    def fetch_user(params):
        """
        Fetches user data from database based on provided params
        """
        try:
            user_object = db.session.query(User).filter_by(**params).first()
            if user_object:
                return user_object
        except Exception as e:
            log.info(e, exc_info=True)
            return False

    @staticmethod
    def generate_auth_token(email_id):
        """
        Generates the Auth Token
        """
        try:
            payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=2, seconds=0),
                "iat": datetime.datetime.utcnow(),
                "sub": email_id,
            }
            return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            log.info(e)

    def create(self):
        """
        Saves the object data to DB and populates ids and dates.
        """
        db.session.add(self)
        db.session.flush()
        db.session.commit()

    def update(self, filter_param, update_params):
        """
        Updates the object data to DB.
        """
        db.session.query(self.__class__).filter_by(**filter_param).update(update_params)
        db.session.commit()

    def delete(self, filter_param):
        """
        Sets status of object as False in DB
        """
        db.session.query(self.__class__).filter_by(**filter_param).update({"deleted_at": self.deleted_at})
        db.session.commit()
