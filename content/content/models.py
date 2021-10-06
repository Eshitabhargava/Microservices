import datetime
import json
import uuid

import glog as log
import jwt
from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, text
from sqlalchemy import Column, String

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from constants import db


class Content(db.Model):
    __tablename__ = "Content"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String())
    story = db.Column(db.String())
    publication_date = db.Column(db.Date())
    publisher_id = db.Column(db.Integer())
    deleted = db.Column(db.String())

    def __init__(self, content_data=None):
        if not content_data:
            content_data = {}
        self.title = str(content_data.get("title"))
        self.story = str(content_data.get("story"))
        self.publication_date = content_data.get("publication_date")
        self.publisher_id = content_data.get("publisher_id")

    def to_response_dict(self):
        """
        Helps json-ify the content object for sending to FE.
        """
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "story": self.story,
            "publication_date": self.publication_date,
            "publication_date": self.publication_date.strftime("%Y-%m-%d"),
            "publisher_id": self.publisher_id
        }
        return resp_dict

    @staticmethod
    def fetch_content(params):
        """
        Fetches Content data from database based on provided params
        """
        try:
            content_object = db.session.query(Content).filter_by(**params).first()
            if content_object:
                return content_object
        except Exception as e:
            log.info(e, exc_info=True)
            return False

    @staticmethod
    def fetch_all(params):
        """
        Fetches all Content objects from Database
        """
        try:
            import pdb;pdb.set_trace()
            sort_by = params.get("sort_by")
            order_by = params.get("order_by")
            order = f"{sort_by} {order_by}"
            content_objects = db.session.query(Content).order_by(text(order)).all()
            if content_objects:
                return content_objects
        except Exception as e:
            log.info(e, exc_info=True)
            return False

    def create(self, caller=""):
        """
        Saves the content data to DB.
        """
        import pdb;pdb.set_trace()
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self.id


    def update(self, filter_param, update_params):
        """
        Updates the content data to DB.
        """
        db.session.query(self.__class__).filter_by(**filter_param).update(update_params)
        db.session.commit()

    def delete(self, filter_param):
        """
        Sets status of object as False in DB
        """
        db.session.query(self.__class__).filter_by(**filter_param).update({"deleted": "True"})
        db.session.commit()
