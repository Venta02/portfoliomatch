"""Smoke tests for the API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "name" in resp.json()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "github_available" in body
    assert "llm_available" in body
