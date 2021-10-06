import flask
import logging as log
from flask_restx import abort
from sqlalchemy import exc


class InvalidEmailError(Exception):
    """Raise for errors when email syntax is not valid"""

    def __init__(self, message="The entered email is invalid"):
        self.message = message
        super().__init__(self.message)
        return abort(400, error=self.message, success=False)


class UserUnauthorizedError(Exception):
    """Raise for errors when user does not have access"""

    def __init__(self, message="The user is not authorized"):
        self.message = message
        super().__init__(self.message)
        return abort(403, error=self.message, success=False)


class UserAlreadyExistsError(Exception):
    """Raise for errors when user already exists."""

    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)
        return abort(409, error=self.message, success=False)


class LoginError(Exception):
    """Raise for errors when user has been logged out."""

    def __init__(self, message="User is not logged in"):
        self.message = message
        super().__init__(self.message)
        return abort(401, error=self.message, success=False)


class AuthError(Exception):
    """Raise for errors when user has been logged out."""

    def __init__(self, message="Auth Failed, Valid username/password required"):
        self.message = message
        super().__init__(self.message)
        return abort(401, error=self.message, success=False)

class AuthTokenError(Exception):
    """Raise for errors related to auth token"""

    def __init__(self, message="Cannot generate Auth Token"):
        self.message = message
        super().__init__(self.message)
        return flask.abort(409, self.message)

class ParameterError(Exception):
    """Raise for errors when all params are not specified"""

    def __init__(self, message="Not enough/ Wrong params entered"):
        self.message = message
        super().__init__(self.message)
        return abort(400, error=self.message, success=False)

class NotFoundError(Exception):
    """Raise for errors when entity not found"""

    def __init__(self, message="Not found"):
        self.message = message
        super().__init__(self.message)
        return abort(400, error=self.message, success=False)