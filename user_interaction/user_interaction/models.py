import datetime
import json
import uuid

import glog as log
import jwt
from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, desc, text

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from constants import db

class Stats(db.Model):
    __tablename__ = "Stats"
    id = Column(SQLAlchemy().Integer, primary_key=True, autoincrement=True)
    content_id = Column(SQLAlchemy().Integer)
    reads = Column(SQLAlchemy().Integer)
    likes = Column(SQLAlchemy().Integer)

    def __init__(self, stats_data=None):
        if not stats_data:
            stats_data = {}
        self.content_id = stats_data.get("content_id")
        self.reads = stats_data.get("reads", 0)
        self.likes = stats_data.get("likes", 0)

    def to_response_dict(self):
        """
        Helps json-ify the user stats object for sending to FE.
        """
        resp_dict = {
            "id": self.id,
            "content_id": self.content_id,
            "reads": self.reads,
            "likes": self.likes
        }
        return resp_dict

    @staticmethod
    def fetch_stats(params):
        """
        Fetches stats data from database based on provided params
        """
        try:
            stats_object = db.session.query(Stats).filter_by(**params).first()
            if stats_object:
                return stats_object
        except Exception as e:
            log.info(e, exc_info=True)
            return False

    @staticmethod
    def fetch_all(params):
        """
        Fetches all Stat objects from Database
        """
        try:
            sort_by = params.get("sort_by")
            if sort_by == 'reads' or sort_by == 'likes':
                order = f"{sort_by} desc"
                stats_objects = db.session.query(Stats).order_by(text(order))
            else:
                stats_objects = db.session.query(Stats).all()
            if stats_objects:
                return stats_objects
        except Exception as e:
            log.info(e, exc_info=True)
            return False

    def create(self):
        """
        Saves the object data to DB
        """
        db.session.add(self)
        db.session.flush()
        db.session.commit()

    def update(self, filter_param, update_params):
        """
        Updates the object data in DB.
        """
        db.session.query(self.__class__).filter_by(**filter_param).update(update_params)
        db.session.commit()

    def delete(self, filter_param):
        """
        Deletes object data in DB.
        """
        db.session.query(self.__class__).filter_by(**filter_param).delete()
        db.session.commit()