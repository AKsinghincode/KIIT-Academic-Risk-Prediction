import os
from flask import Flask

def create_app():
    # Explicitly calculate absolute path to app/templates
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'edurisk-secret-key'

    # Register Blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.predict_routes import predict_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(predict_bp)

    return app