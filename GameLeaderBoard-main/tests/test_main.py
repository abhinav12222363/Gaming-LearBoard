from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_submit_score():
    res = client.post("/api/leaderboard/submit", json={"user_id": 123, "score": 100})
    assert res.status_code == 200
    assert res.json()["message"] == "Score submitted successfully"

def test_get_leaderboard():
    res = client.get("/api/leaderboard/top")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_rank():
    res = client.get("/api/leaderboard/rank/123")
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == 123
    assert "rank" in data
    assert "total_score" in data
