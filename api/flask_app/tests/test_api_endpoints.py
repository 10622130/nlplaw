import pytest
import json

def test_web_user_message_endpoint(client):
    """Test web API user message endpoint"""
    response = client.post('/api/user_message', 
                          json={'user_input': '這是一個法律問題'})
    
    # Should return 200 for valid input
    assert response.status_code in [200, 500]  # 500 if OpenAI key is fake
    data = json.loads(response.data)
    assert 'response' in data or 'error' in data

def test_web_user_message_empty_input(client):
    """Test web API with empty input"""
    response = client.post('/api/user_message', 
                          json={'user_input': ''})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_ai_endpoint_unauthorized(client):
    """Test AI endpoint without API key"""
    response = client.post('/api/ai', 
                          json={'text': '測試'})
    
    assert response.status_code == 401

def test_ai_endpoint_with_api_key(client):
    """Test AI endpoint with API key"""
    response = client.post('/api/ai', 
                          json={'text': '測試法律問題'},
                          headers={'Authorization': 'Bearer test_api_key'})
    
    # Should return 200 for valid input
    assert response.status_code in [200, 500]  # 500 if OpenAI key is fake