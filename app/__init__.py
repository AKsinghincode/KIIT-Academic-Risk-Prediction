import os
from flask import Flask
from app.database import close_db

def create_app():
    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-secret'),
        DATABASE_PATH=os.environ.get('DATABASE_PATH', '/tmp/database.sqlite')
    )

    app.teardown_appcontext(close_db)

    # Register Predict Blueprint
    from app.routes.predict_routes import predict_bp
    app.register_blueprint(predict_bp)

    # Register Dashboard Blueprint
    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app