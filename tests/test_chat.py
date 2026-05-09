from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_basic():
    payload = {
        "user": "alice",
        "message": "hello"
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    assert "answer" in r.json()