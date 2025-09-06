import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Simple configuration class"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LINE Bot
    CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', '')
    CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # API
    API_KEY = os.environ.get('API_KEY', '')
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Flask
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
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