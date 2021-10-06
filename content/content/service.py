from datetime import date
import os
import json

import requests
from flask_restx import Namespace, Resource, fields
from flask import Response, current_app, request
from numpy import genfromtxt
import glog as log

import content.exceptions as exceptions
import content.models as models
from content.validator import validate_params

content_namespace = Namespace("content")

content_creation_model = content_namespace.model(
    "ContentCreationController",
    {
        "content": fields.Raw(required=True),
        "publisher_id": fields.String(required=True)
    },
    )

content_updation_model = content_namespace.model(
    "ContentController",
    {
        "content": fields.Raw(),
        "publisher_id": fields.String()
    },
    )


class FetchStats:
    @staticmethod
    def fetch_stats(sort_by, order_by):
        url = f"http://127.0.0.1:8000/stats/all??sort_by=sort_by&order_by=order_by"
        response = requests.get(url)
        if response.ok:
            stats = response.content.decode('utf-8')
            return stats

class Validator:
    @staticmethod
    def validate_user_id(user_id):
        url = f"http://127.0.0.1:5000/user/{user_id}/validate"
        user_exists = requests.get(url)
        if user_exists.ok:
            user_exists = json.loads(user_exists.content.decode('utf-8'))
            if user_exists["data"] != "True":
                return False
        return True

@content_namespace.route("")
class ContentCreationController(Resource):
    @content_namespace.expect(content_creation_model, validate=False)
    @validate_params(content_updation_model)
    def post(self, *args, **kwargs):
        """
        Creates new Content object
        """
        content_data = kwargs.get("params")
        content_file = content_data.get("content")
        data = file_loader(content_file)
        # data injestion logic
        response = {}
        data["publication_date"] = date.today()
        # validate user id
        publisher_id = int(content_data.get("publisher_id"))
        user_id_valid = Validator.validate_user_id(publisher_id)
        if not user_id_valid:
            response["message"] = "Invalid Publisher id"
            return Response(
                response=json.dumps(obj=response),
                status=400,
                mimetype="application/json"
            )
        data["publisher_id"] = publisher_id
        content_id = models.Content(content_data=data).create()
        response["data"] = f"Content created successfully with id- {content_id}"
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )


@content_namespace.route("/<int:content_id>")
class ContentController(Resource):
    @content_namespace.expect(content_updation_model, validate=False)
    @validate_params(content_updation_model)
    def put(self, *args, **kwargs):
        """
        Updates content in db
        """
        content_id = kwargs.get("content_id")
        content_data = kwargs.get("params")
        if not content_data:
            raise exceptions.ParameterError("No data to update")
        content_obj = models.Content.fetch_content({"id": content_id})
        if not content_obj:
            log.warning("Content object with given id does not exist")
            raise exceptions.NotFoundError("Content object with given id does not exist")
        # data injestion
        data = {}
        if content_data.get("content"):
            data = file_loader(content_data.get("content")) 
        if content_data.get("publisher_id"):
            publisher_id = int(kwargs.get("publisher_id"))
            user_id_valid = Validator.validate_user_id(publisher_id)
            if type(user_id_valid) is dict:
                return user_id_valid
            data["publisher_id"] = publisher_id
        models.Content().update(filter_param= {"id": content_id},update_params=data)
        response = {}
        response["data"] = f"Content modified successfully"
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )

    def get(self, *args, **kwargs):
        """
        Fetches Content data
        """
        import pdb;pdb.set_trace()
        content_id = kwargs.get("content_id")
        content_obj = models.Content.fetch_content({"id": content_id})
        if not content_obj:
            log.warning("Content does not exist")
            raise exceptions.NotFoundError("content with given Id not found")
        response = {}
        response["data"] = content_obj.to_response_dict()
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )

    def delete(self, *args, **kwargs):
        """
        Deletes content data
        """
        content_id = kwargs.get("content_id")
        content_obj = models.Content.fetch_content({"id": content_id})
        if not content_obj:
            log.warning("Content does not exist")
            raise exceptions.NotFoundError("content with given Id not found")
        content_obj.delete(filter_param= {"id": content_id})
        response = {}
        response["message"] = "Content object deleted successfully"
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )


@content_namespace.route("/all")
class FetchContentController(Resource):
    def get(self, *args, **kwargs):
        """
        Fetches Content data
        """
        sort_by = request.args.get("sort_by")
        order_by = request.args.get("order_by")
        response = {}
        if sort_by == 'top':
            stats = FetchStats.fetch_stats(sort_by, order_by)
            response["status"] = 200
            response["data"] = stats["data"]
            return response
        elif sort_by == 'publication_date':
            content_objs = models.Content.fetch_all({"sort_by": sort_by, "order_by": order_by})
        if not content_objs:
            log.warning("Content does not exist")
            raise exceptions.NotFoundError("No Content found")
        response["data"] = []
        for content_obj in content_objs:
            response["data"].append(content_obj.to_response_dict())
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )

@content_namespace.route("/<int:content_id>/validate")
class ContentValidationController(Resource):
    def get(self, *args, **kwargs):
        """
        Validates existence of content object with given id
        """
        content_id = kwargs.get("content_id")
        content_obj = models.Content.fetch_content({"id": content_id})
        response = {}
        if not content_obj:
            response["data"] = "False"
        else:
            response["data"] = "True"
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )

def file_loader(file):
    data_dict = {}
    file_name = file.filename
    content_file.save(os.path.join(os.getcwd(), filename))
    data = genfromtxt(file_name, delimiter=',', converters={0: lambda s: str(s)})
    data = data.tolist()
    data_dict ["title"] = data[0]
    data_dict ["content"] = data[1]
    return data_dict
