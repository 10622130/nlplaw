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
load_dotenv()

#print("Current working directory:", os.getcwd())

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', '')
app.config['CHANNEL_SECRET'] = os.environ.get('CHANNEL_SECRET', '')
app.config['CHANNEL_ACCESS_TOKEN'] = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')


db.init_app(app)
migrate = Migrate(app, db)

# 註冊 Blueprint，API 路徑採用階層式設計
app.register_blueprint(linebot_bp)
app.register_blueprint(ai_bp, url_prefix="/api")
app.register_blueprint(web_bp, url_prefix="/api")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5002, debug=True)

