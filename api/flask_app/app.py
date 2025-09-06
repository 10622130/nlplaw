from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
import os

from config import Config
from models import db
from blueprints import ai_bp, linebot_bp, web_bp

def create_app():
    """Create and return a Flask app instance with all configurations"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    Config.validate_config()
    
    # CORS settings
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize database and migration
    db.init_app(app)
    Migrate(app, db)
    
    
    # Register blueprints
    app.register_blueprint(linebot_bp)
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(web_bp, url_prefix="/api")
    
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Run in debug mode based on environment
    app.run(port=5002, debug=app.config['DEBUG'])