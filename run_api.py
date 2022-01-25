"""
This file is the entry point of flask api. Launch python3 ronoco_vm/run.py to run flask server
"""
import os

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.debug import DebuggedApplication


class ReachyRunAPI:
    """
    Define and setup flask server and ros topic subscriber / publisher for ronoco-vm
    """

    def __init__(self):
        """
        Launch flask server when RonocoVm is created (this constructor uses SocketIO)
        """
        self.app = None
        self.create_app()
        socketio = SocketIO(self.app, logger=False, cors_allowed_origins='*')
        self.setup_app()
        socketio.run(self.app, host="0.0.0.0")

    def create_app(self, test_config=None):
        """
        Build a Flask instance and configure it
        :param test_config: path to configuration file (Default : None)
        :return: a Flask instance
        """
        # create and configure the app
        self.app = Flask(__name__, instance_relative_config=True)
        self.app.config.from_mapping(
            SECRET_KEY='dev',
        )
        self.app.debug = True
        self.app.wsgi_app = DebuggedApplication(self.app.wsgi_app, evalex=True)

        if test_config is None:
            # load the instance config, if it exists, when not testing
            self.app.config.from_pyfile('config.py', silent=True)
        else:
            # load the test config if passed in
            self.app.config.from_mapping(test_config)

        # ensure the instance folder exists
        try:
            os.makedirs(self.app.instance_path)
        except OSError:
            pass

    def setup_app(self):
        """
        Register blueprint in app.
        The class attribute "app" must contain an Flask instance
        :return: None
        """
        import api
        self.app.register_blueprint(api.ReachyAPI().bp)
        CORS(self.app)


if __name__ == "__main__":
    ReachyRunAPI()
