from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from app.config import Config
from app.extensions import db, bcrypt, ma

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    Migrate(app, db)

    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    # Import models so Flask-Migrate sees them
    from . import models
    
    # Create Flask-RESTful API instance
    api = Api(app)
    
    # Register routes
    from .routes import initialize_routes
    initialize_routes(api)  # Pass api, not app

    return app