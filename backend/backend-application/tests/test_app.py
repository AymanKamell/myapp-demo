import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2

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


@patch("app.psycopg2.connect")
def test_database(mock_connect, monkeypatch):
    monkeypatch.setenv("DB_HOST", "test-host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test-db")
    monkeypatch.setenv("DB_USER", "test-user")
    monkeypatch.setenv("DB_PASSWORD", "unused")

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = ("test-db", "test-user")
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    client = app.test_client()

    response = client.get("/api/db")

    assert response.status_code == 200
    assert response.json == {
        "database": "test-db",
        "user": "test-user",
        "status": "connected",
    }

    mock_connect.assert_called_once_with(
        host="test-host",
        port="5432",
        database="test-db",
        user="test-user",
        password="unused",
    )

    mock_cursor.execute.assert_called_once_with(
        "SELECT current_database(), current_user;"
    )

    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()


@patch("app.psycopg2.connect")
def test_database_error(mock_connect, monkeypatch):
    monkeypatch.setenv("DB_HOST", "test-host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test-db")
    monkeypatch.setenv("DB_USER", "test-user")
    monkeypatch.setenv("DB_PASSWORD", "unused")

    mock_connect.side_effect = psycopg2.Error("database connection failed")

    client = app.test_client()

    response = client.get("/api/db")

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert response.json["message"] == "database connection failed"
