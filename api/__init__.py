import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import DevelopmentConfig, AcceptanceConfig, ProductionConfig

from swagger import init_swagger


db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'acceptance':
        app.config.from_object(AcceptanceConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        raise ValueError(f"Invalid configuration name: {config_name}")

    # Initialize extensions
    db.init_app(app)
    swagger = init_swagger(app)

    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
