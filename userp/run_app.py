import argparse
import json
import os
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import init, migrate, upgrade, Migrate
from flask_restx import Api
from flask import request
from user.service import user_namespace
import glob
import logging as log
from constants import ADD_MODELS, PROTECTED_PATH, db


LOG = log.getLogger('werkzeug')


class BaseManager:
    def __init__(self):
        self.SECRET_KEY, self.PORT = None, None
        # Core logic function
        self.log = LOG
        self.log.info("Reading configs")
        self.parse_config()

    def initialize_managerconfig(self):
        Migrate(self.app, db, compare_type=True)

    @staticmethod
    def add_migrate_args(subparser):
        # Add your own subparser using the subparser object
        migrate_parser = subparser.add_parser("migrate", help="migrations commands")
        migrate_parser.add_argument("--init", action="store_true")
        migrate_parser.add_argument("--migrate", action="store_true")
        migrate_parser.add_argument("--upgrade", action="store_true")

    @staticmethod
    def add_run_args(subparser):
        subparser.add_parser("run", help="run the application")

    def parse_config(self):
        parser = argparse.ArgumentParser()
        # Add default normal arguments here
        parser.add_argument(
            "-ac",
            "--appconfig",
            help="configuration file to run the application",
            required=True,
        )
        subparser = parser.add_subparsers(dest="command")
        # Make False to make subsparser commands optional
        subparser.required = True
        # Initialize subparser
        BaseManager.add_run_args(subparser)
        BaseManager.add_migrate_args(subparser)
        self.args = parser.parse_args()
        try:
            with open(self.args.appconfig, "r") as con:
                self.configs = json.load(con)
        except Exception as e:
            self.log.error("Error: {}".format(e))
            exit(1)

        self._prepare_app()
        # Check subparser commands and do the process
        if self.args.command == "migrate":
            with self.app.app_context():
                if self.args.init:
                    init()
                elif self.args.migrate:
                    mig_models = glob.glob("{}/app/models/*.py".format(os.getcwd()))
                    mig_models = [_m.split("/")[-1] for _m in mig_models]
                    mig_models = ", ".join([_m.split(".")[0] for _m in mig_models if _m != "base.py"])
                    os.system(ADD_MODELS.format(mig_models))
                    migrate()
                elif self.args.upgrade:
                    upgrade()

        # Run the application
        if self.args.command == "run":
            self.run()

    def _prepare_app(self):
        # Create attributes from json
        self.create_vars(self.configs)
        # Basic app object creation
        self.app = self.create_app()
        self.app.logger = LOG
        # Creating API object with error handlers
        self.api = Api(self.app)
        # Initialize namespaces in this method.
        self.initialize_namespaces()
        # Manager related config
        self.initialize_managerconfig()
        # set env variables
        self._set_env_variables()

    def create_vars(self, configs):
        # Creating attributes from config file
        for k, v in configs.items():
            setattr(self, k.upper(), v)
        self.check_configs()

    def run(self):
        # Running the application
        self.app.run(port=5000)

    def create_app(self):
        app = FlaskAPI(__name__, instance_relative_config=True, instance_path=PROTECTED_PATH)
        self.initialize_models(app)
        CORS(app)
        return app

    def initialize_models(self, app):
        # Use the same or modify your db or app config here.
        app.config["COMPRESS_REGISTER"] = False
        app.config["COMPRESS_ALGORITHM"] = "gzip"
        app.config["COMPRESS_MIMETYPES"] = ["image/svg+xml"]
        app.config["SECRET_KEY"] = self.SECRET_KEY
        app.config["SQLALCHEMY_DATABASE_URI"] = self.DB_CONNECTION_STRING
        app.config["DB_CONNECTION_POOL"] = self.DB_CONNECTION_POOL
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = self.SQLALCHEMY_TRACK_MODIFICATIONS
        db.init_app(app)
        return

    def initialize_namespaces(self):
        # This will initialize all the namespaces
        # Create namespaces
        self.api.add_namespace(ns=user_namespace)

    def _set_env_variables(self):
        os.environ["SECRET_KEY"] = self.SECRET_KEY

    def check_configs(self):
        # Check and throw error if you want here on configs
        try:
            if not self.SECRET_KEY:
                raise Exception("A secret key is must for application to access session")
        except Exception as e:
            print(e)
            exit(2)


if __name__ == "__main__":
    BaseManager()