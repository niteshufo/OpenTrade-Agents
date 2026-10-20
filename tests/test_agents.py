from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_agent():
    response = client.post(
        "/api/v1/agents/register",
        json={
            "name": "test-momentum-agent",
            "description": "Momentum strategy test",
            "strategy_type": "momentum",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "test-momentum-agent"


def test_duplicate_agent_rejected():
    payload = {
        "name": "duplicate-test-agent",
        "description": "Duplicate test",
        "strategy_type": "momentum",
    }

    first = client.post("/api/v1/agents/register", json=payload)
    second = client.post("/api/v1/agents/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_invalid_agent_rejected():
    response = client.post(
        "/api/v1/agents/register",
        json={
            "name": "x",
            "description": "",
            "strategy_type": "momentum",
        },
    )

    assert response.status_code == 422
