from flask import Flask
from app.config import get_config



def create_app():

    app = Flask(__name__)
    app.config.from_object(get_config())

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import users_bp
    from app.routes.techniques_routes import techniques_bp
    from app.routes.reviews_routes import reviews_bp
    from app.routes.gyms_routes import gyms_bp
    from app.routes.gym_reviews_routes import gym_reviews_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(techniques_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(gyms_bp)
    app.register_blueprint(gym_reviews_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
