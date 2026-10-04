from flask import Flask
from app.database import close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Register database teardown
    app.teardown_appcontext(close_db)

    from app.routes.predict_routes import predict_bp
    app.register_blueprint(predict_bp)

    return app