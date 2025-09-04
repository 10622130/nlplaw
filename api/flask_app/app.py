# app.py
from flask import Flask
from flask_migrate import Migrate
from models import db
from linebot_bp import linebot_bp
from ai_bp import ai_bp
from web_bp import web_bp
import os
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    """
    Create and return a Flask app instance, including all initialization settings and security checks.
    """
    load_dotenv()

    app = Flask(__name__)

    # CORS settings: change '*' to specific domains in production for better security
    CORS(app, resources={r"/*": {"origins": os.environ.get('CORS_ORIGINS', '*')}})

    # set Flask config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', '')
    app.config['CHANNEL_SECRET'] = os.environ.get('CHANNEL_SECRET', '')
    app.config['CHANNEL_ACCESS_TOKEN'] = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

    # check required envs
    required_envs = [
        'SQLALCHEMY_DATABASE_URI',
        'CHANNEL_SECRET',
        'CHANNEL_ACCESS_TOKEN',
        'OPENAI_API_KEY'
    ]
    missing_envs = [key for key in required_envs if not app.config.get(key)]
    if missing_envs:
        raise RuntimeError(f"Missing envs: {', '.join(missing_envs)}")

    # initialize database and migration
    db.init_app(app)
    Migrate(app, db)

    # register blueprints
    app.register_blueprint(linebot_bp)
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(web_bp, url_prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # only for local testing
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(port=5002, debug=debug_mode)
