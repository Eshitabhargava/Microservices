import os

from flask import request, g
from flask_restx import abort
from decorator import decorator
import jwt

import user_interaction.models as models
import user_interaction.exceptions as exceptions

type_maps = {
    "string": str,
    "integer": int,
    "boolean": bool,
}

def validate_params(params):
    """
    A decorator which checks and stops execution if the params are invalid
    """

    def validate(function, *args, **kwargs):
        json_obj = {}
        if request.method == "HEAD" or request.method == "OPTIONS":
            return function(*args, **kwargs)
        elif request.args:
            json_obj.update(request.args)
        elif request.json:
            json_obj.update(request.json)
        elif request.content_type and "multipart/form-data" in request.content_type:
            if getattr(request, "files"):
                json_obj.update(request.files)
            if getattr(request, "data"):
                json_obj.update(request.data.to_dict())
        elif request.method == "DELETE":
            json_obj = json_obj
        kwargs["params"] = json_obj
        response = check_missing_params(params, json_obj)
        if not response == {}:
            return abort(400, error=response, success=False)
        response = check_incorrect_types(params, json_obj)
        if not response == {}:
            return abort(400, error=response, success=False)
        return function(*args, **kwargs)

    return decorator(validate)

def check_missing_params(params, filtered_params):
    response = {}
    missing = [
        r for r in params.keys() if params[r].required and r not in filtered_params
    ]
    if missing:
        response = {
            "message": "payload missing required params",
            "missing": ",".join(missing),
        }
    return response
        
def check_incorrect_types(params, filtered_params):
    response = {}
    wrong_types = [
        r
        for r in params.keys()
        if params[r].required
        and not isinstance(filtered_params[r], type_maps.get(params[r].__schema_type__))
    ]
    if wrong_types:
        response = {
            "message": "payload type error",
            "param_types": {
            k: str(params[k].__schema_type__) for k in params.keys()
            },
        }
    return response
