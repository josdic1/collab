from flask import Flask
from flask_migrate import Migrate
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
         origins=["https://files.demberry.com"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    
    from . import models
    from .routes import initialize_routes
    initialize_routes(app)
    
    return app