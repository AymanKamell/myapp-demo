import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_message():
    client = app.test_client()

    response = client.get("/api/message")

    assert response.status_code == 200
    assert response.json["message"] == "Hello from the Kubernetes backend!"
