import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Simple configuration class"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask session
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')

    # LINE Bot (Messaging API)
    CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', '')
    CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', '')

    # LINE Login (OAuth 2.0)
    LINE_LOGIN_CHANNEL_ID = os.environ.get('LINE_LOGIN_CHANNEL_ID', '')
    LINE_LOGIN_CHANNEL_SECRET = os.environ.get('LINE_LOGIN_CHANNEL_SECRET', '')
    LINE_LOGIN_REDIRECT_URI = os.environ.get('LINE_LOGIN_REDIRECT_URI', 'http://localhost:5002/auth/line/callback')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', '/')
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Exam API
    EXAM_API_URL = os.environ.get('EXAM_API_URL', '')
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')
    
    # Flask
    DEBUG = os.environ.get('FLASK_ENV') == 'dev'
    
    # Required environment variables
    REQUIRED_ENV_VARS = [
        'SQLALCHEMY_DATABASE_URI',
        'CHANNEL_SECRET', 
        'CHANNEL_ACCESS_TOKEN',
        'OPENAI_API_KEY'
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are present"""
        missing_vars = []
        for var in cls.REQUIRED_ENV_VARS:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
        

