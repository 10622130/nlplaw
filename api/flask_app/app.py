from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
import click
import os
import logging
from api.flask_app.config import Config
from api.flask_app.models import db
from api.flask_app.routes import ai_bp, linebot_bp, web_bp, auth_bp


logging.basicConfig(level=logging.INFO)


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

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(linebot_bp)
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(web_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)
    
    @app.cli.command("setup-richmenu")
    @click.argument("main_image")
    @click.argument("exam_image")
    def setup_richmenu(main_image, exam_image):
        """Set up LINE Rich Menus. Args: path to main.jpg and exam.jpg"""
        from core.richmenu import setup_main_menu, setup_exam_menu
        token = app.config["CHANNEL_ACCESS_TOKEN"]
        main_id = setup_main_menu(token, main_image)
        click.echo(f"主選單建立完成: {main_id}")
        exam_id = setup_exam_menu(token, exam_image)
        click.echo(f"考題選單建立完成: {exam_id}")

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Run in debug mode based on environment
    app.run(port=5002, debug=app.config['DEBUG'])