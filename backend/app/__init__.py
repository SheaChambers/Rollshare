from flask import Flask
from .config import get_config


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
