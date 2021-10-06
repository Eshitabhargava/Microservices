import os
import json

import requests
from flask_restx import Namespace, Resource, fields
from flask import Response, current_app, request
import glog as log

import user_interaction.exceptions as exceptions
import user_interaction.models as models
from user_interaction.validator import validate_params

stats_namespace = Namespace("stats")

stats_modification_model = stats_namespace.model(
    "StatsController",
    {
        "content_id": fields.Integer(required=True),
        "event_name": fields.String(required=True)
    },
)

fetch_stats_model = stats_namespace.model(
    "StatsController",
    {
        "filter": fields.String(required=True),
        "order_by": fields.String()
    },
)

class Validator:
    @staticmethod
    def validate_content_id(content_id):
        url = f"http://127.0.0.1:3000/content/{content_id}/validate"
        content_exists = requests.get(url)
        if content_exists.ok:
            content_exists = json.loads(content_exists.content.decode('utf-8'))
            if content_exists["data"] != "True":
                return False
        return True

@stats_namespace.route("/<int:content_id>/<string:event>")
class StatsController(Resource):
    def put(self, *args, **kwargs):
        """
        Updates user interaction stats
        """
        content_id = kwargs.get("content_id")
        event = kwargs.get("event")
        response = {}
        # verify content id
        content_id_valid = Validator.validate_content_id(content_id)
        if not content_id_valid:
            response["message"] = "Invalid Publisher id"
            response["success"] = "False"
            return Response(
                response=json.dumps(obj=response),
                status=400,
                mimetype="application/json"
            )
        stats_obj = models.Stats.fetch_stats({"content_id": content_id})
        stats_data ={}
        import pdb;pdb.set_trace()
        if stats_obj:
            if event.lower() == 'read':
                stats_data["reads"] = stats_obj.reads+1
            elif event.lower() == 'like':
                stats_data["likes"] = stats_obj.likes+1
            else:
                status = 400
                response["message"] = "Invalid user interaction event"
                response["success"] = "False"
            models.Stats().update(filter_param={"content_id": content_id}, update_params=stats_data)
        else:       
            stats_data = {
                "content_id": content_id
            }
            if event.lower() == 'read':
                stats_data["reads"] = 1
                stats_data["likes"] = 0
            elif event.lower() == 'like':
                stats_data["likes"] = 1
                stats_data["reads"] = 0
            else:
                response["message"] = "Invalid user interaction event"
                response["success"] = "False"
                return Response(
                    response=json.dumps(obj=response),
                    status=400,
                    mimetype="application/json"
                )
            models.Stats(stats_data=stats_data).create()
        status = 200
        response["message"] = "Content Interaction stats updated Successfully"
        response["success"] = "True"
        return Response(
                response=json.dumps(obj=response),
                status=status,
                mimetype="application/json"
            )


    def get(self, *args, **kwargs):
        content_id = kwargs.get("content_id")
        event = kwargs.get("event")
        response = {}
        status = 200
        content_id_valid = Validator.validate_content_id(content_id)
        if not content_id_valid:
            response["message"] = "Invalid Publisher id"
            return Response(
                response=json.dumps(obj=response),
                status=400,
                mimetype="application/json"
            )
        stats_obj = models.Stats.fetch_stats({"content_id": content_id})
        if not stats_obj:
            response["message"] = "No Interaction stats found for given content"
        response["data"] = {}
        if event.lower() == 'read':
            response["data"]["reads"] = stats_obj.reads
        elif event.lower() == 'like':
            response["data"]["likes"] = stats_obj.likes
        elif event.lower() == 'all':
            response["data"] = stats_obj.to_response_dict()
        else:
            status = 400
            response["message"] = "Invalid user interaction event"
        return Response(
                response=json.dumps(obj=response),
                status=status,
                mimetype="application/json"
            )

@stats_namespace.route("/<int:content_id>")
class StatsDeletionController(Resource):
    def delete(self, *args, **kwargs):
        content_id = kwargs.get("content_id")
        response = {}
        status = 200
        content_id_valid = Validator.validate_content_id(content_id)
        if not content_id_valid:
            response["success"] = "False"
            response["message"] = "Invalid Publisher id"
            return Response(
                response=json.dumps(obj=response),
                status=400,
                mimetype="application/json"
            )
        stats_obj = models.Stats().delete(filter_param={"content_id": content_id})
        response["message"] = f"Stats for content id- {content_id} deleted successfully."
        response["success"] = "True"
        return Response(
                response=json.dumps(obj=response),
                status=400,
                mimetype="application/json"
            )

@stats_namespace.route("/all")
class FetchStatsController(Resource):
    def get(self, *args, **kwargs):
        _filter = request.args.get("filter")
        sort_by = request.args.get("sort_by")
        response = {}
        params = {}
        if _filter == 'top':
            params["sort_by"] = sort_by
        contents_stats = models.Stats.fetch_all(params)
        if not contents_stats:
            response["message"] = "No data available"
        else:
            response["success"] = "True"
            response["data"] = []
            for content_stat in contents_stats:
                response["data"].append(content_stat.to_response_dict())
        return Response(
            response=json.dumps(obj=response),
            status=200,
            mimetype="application/json"
        )
        