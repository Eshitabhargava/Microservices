from flask_restx import Api, Resource

from .service import user_namespace

api = Api()
api.add_namespace(user_namespace)