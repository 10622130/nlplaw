import pytest
import os
from app import create_app
from models import db

@pytest.fixture
def app():
    """Create application for testing"""
    # Set test environment variables BEFORE creating app
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['CHANNEL_SECRET'] = 'test_secret'
    os.environ['CHANNEL_ACCESS_TOKEN'] = 'test_token'
    os.environ['OPENAI_API_KEY'] = 'test_openai_key'
    os.environ['API_KEY'] = 'test_api_key'
    
    app = create_app()
    app.config['TESTING'] = True
    # Override config after app creation
    app.config['API_KEY'] = 'test_api_key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI test runner"""
    return app.test_cli_runner()