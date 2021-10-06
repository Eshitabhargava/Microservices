import re

from flask_restx import Namespace, Resource, fields, abort
from flask_bcrypt import Bcrypt
from flask import Response
import logging as log

import user.exceptions as exceptions
import user.models as models
from user.validator import validate_params, decode_auth_token

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from constants import EMAIL_REGEX

user_namespace = Namespace("user")

user_model = user_namespace.model(
    "UserController",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True)
    },
)

user_creation_model = user_namespace.model(
    "UserCreationController",
    {
        "email": fields.String(required=True),
        "first_name": fields.String(required=True),
        "last_name": fields.String(required=True),
        "phone_number": fields.String(required=True),
        "password": fields.String(required=True)
    },
)

user_updation_model = user_namespace.model(
    "UserUpdationController",
    {
        "first_name": fields.String(),
        "last_name": fields.String(),
        "phone_number": fields.String(),
        "password": fields.String()
    },
)


@user_namespace.route("/register")
class UserCreationController(Resource):
    @user_namespace.expect(user_creation_model, validate=False)
    @validate_params(user_creation_model)
    def post(self, *args, **kwargs):
        """
        Creates new user account
        """
        user_data = kwargs.get("params")
        if not EMAIL_REGEX.fullmatch(user_data.get("email", "")):
            log.warning("The entered email is invalid - {}".format(user_data.get("email")))
            raise exceptions.InvalidEmailError
        user_object = models.User.fetch_user({"email": user_data.get("email")})
        if user_object:
            log.warning("Users already exists - {}".format(user_data.get("email")))
            raise exceptions.UserAlreadyExistsError
        models.User(user_data=user_data).create()
        user_object = models.User.fetch_user({"email": user_data.get("email")})
        response = {}
        response["status"] = 200
        response["message"] = f"User - {user_object.email} Registered Successfully with id - {user_object.id}"
        return response


@user_namespace.route("/login")
class LoginController(Resource):
    @user_namespace.expect(user_model, validate=False)
    @validate_params(user_model)
    def post(self, *args, **kwargs):
        """
        Login the user if credentials are valid
        """
        post_data = kwargs.get("params")
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not EMAIL_REGEX.fullmatch(post_data.get("email")):
            raise exceptions.InvalidEmailError
        user_obj = models.User.fetch_user({"email": post_data.get("email")})
        if not user_obj:
            raise exceptions.NotFoundError(message="check credentials: user email not found")
        is_valid_password = Bcrypt().check_password_hash(user_obj.password, post_data.get("password"))
        if not is_valid_password:
            log.warning("Auth Failed, Valid username/password required - {}".format(post_data.get("password")))
            raise exceptions.AuthError
        auth_token = user_obj.generate_auth_token(user_obj.email)
        if not auth_token:
            log.warning("Cannot generate Auth Token")
            raise exceptions.AuthTokenGenError
        data = {"auth_token": auth_token.decode()}
        response = {}
        response["status"] = 200
        response["message"] = "Authentication Successful"
        response["data"] = data
        return response


@user_namespace.route("/<int:user_id>")
class UserController(Resource):
    @user_namespace.expect(user_updation_model, validate=False)
    @validate_params(user_updation_model)
    @decode_auth_token
    def put(self, *args, **kwargs):
        """
        Updates user data
        """
        user_data = kwargs.get("params")
        user_id = kwargs.get("user_id")
        if not user_data:
            raise exceptions.ParameterError("No data to update")
        user_obj = models.User.fetch_user({"id": user_id})
        if not user_obj:
            log.warning("user does not exist")
            raise exceptions.NotFoundError("user does not exist")
        if "password" in user_data:
            user_data["password"] = Bcrypt().generate_password_hash(
                user_data.get("password")
                ).decode()
        models.User().update(filter_param= {"id": user_id},update_params=user_data)
        response = {}
        response["status"] = 200
        response["message"] = "Users Details modified successfully"
        return response

    @decode_auth_token
    def delete(self, *args, **kwargs):
        """
        Deletes user data
        """
        user_id = kwargs.get("user_id")
        user_obj = models.User.fetch_user({"id": user_id})
        if not user_obj:
            log.warning("user does not exist")
            raise exceptions.NotFoundError("user does not exist")
        user_obj.delete()
        response = {}
        response["status"] = 200
        response["message"] = "User deleted successfully"
        return response

    @decode_auth_token
    def get(self, *args, **kwargs):
        """
        Fetches user data
        """
        user_id = kwargs.get("user_id")
        user_obj = models.User.fetch_user({"id": user_id})
        if not user_obj:
            log.warning("User does not exist")
            raise exceptions.NotFoundError("User with given Id not found")
        response = {}
        response["status"] = 200
        response["data"] = user_obj.to_response_dict()
        return Response(
        response=json.dumps(obj=response),
        status=status,
        mimetype="application/json",
        headers=BASE_HEADERS,
    )
        return response
        
@user_namespace.route("/<int:user_id>/validate")
class UserValidationController(Resource):
    def get(self, *args, **kwargs):
        """
        Fetches user data
        """
        user_id = kwargs.get("user_id")
        user_obj = models.User.fetch_user({"id": user_id})
        response = {}
        response["status"] = 200
        if not user_obj:
            response["data"] = "False"
        else:
            response["data"] = "True"
        return response