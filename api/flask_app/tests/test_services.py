import pytest
from services import UserService, AIService
from models import db, User

def test_user_service_create_user(app):
    """Test user creation service"""
    with app.app_context():
        user = UserService.create_user_if_not_exists("test_user_123")
        assert user.id == "test_user_123"
        assert UserService.user_exists("test_user_123") == True

def test_user_service_save_input(app):
    """Test saving user input"""
    with app.app_context():
        UserService.create_user_if_not_exists("test_user_123")
        user_input = UserService.save_user_input("test_user_123", "測試問題", "測試回答")
        
        assert user_input.user_id == "test_user_123"
        assert user_input.input_text == "測試問題"
        assert user_input.ai_response == "測試回答"

def test_ai_service_validate_input_length():
    """Test AI service input length validation"""
    assert AIService.validate_input_length("短問題") == True
    assert AIService.validate_input_length("很"*201) == False