import os

from flask import request, g
from flask_restx import abort
from decorator import decorator
import jwt

import user.models as models
import user.exceptions as exceptions

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

@decorator
def decode_auth_token(f, *args, **kwargs):
    """
    Decorator for views that require a certain permission of the logged in
    user.
    """
    if "AUTHORIZATION" in request.headers or "auth_token" in request.view_args:
        auth_token = request.headers.get('AUTHORIZATION') or request.view_args.get('auth_token')
        if auth_token:
            try:
                payload = jwt.decode(auth_token, os.getenv("SECRET_KEY"))
            except exceptions.AuthError(message="Signature expired, login again"):
                return response_dict(status=400, message="Signature expired, login again")
            email = payload["sub"]
            user_obj = models.User.fetch_user({"email": email})
            if not user_obj:
                raise exceptions.UserUnauthorizedError(message="Authentication failed")
            kwargs["id"] = user_obj.id
            kwargs["email"] = email
            g.user_id = user_obj.id
        return f(*args, **kwargs)
    raise NoAuthTokenPresentError