from flask import Flask
from dotenv import load_dotenv
from .config import get_config



def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(get_config())

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
