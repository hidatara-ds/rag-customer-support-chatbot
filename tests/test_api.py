"""
Basic API tests for the chatbot application.
Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data


def test_products_endpoint():
    """Test products listing endpoint"""
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_chat_endpoint_validation():
    """Test chat endpoint input validation"""
    # Empty user
    response = client.post("/chat", json={"user": "", "message": "test"})
    assert response.status_code == 422 or response.status_code == 400
    
    # Empty message
    response = client.post("/chat", json={"user": "test", "message": ""})
    assert response.status_code == 422 or response.status_code == 400
    
    # Missing fields
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_endpoint_success():
    """Test successful chat interaction"""
    response = client.post(
        "/chat",
        json={"user": "test_user", "message": "Hello"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_orders_endpoint():
    """Test orders endpoint"""
    response = client.get("/orders/test_user")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
