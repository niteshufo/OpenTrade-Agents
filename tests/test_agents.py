

def test_register_agent(client):
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


def test_duplicate_agent_rejected(client):
    payload = {
        "name": "duplicate-test-agent",
        "description": "Duplicate test",
        "strategy_type": "momentum",
    }

    first = client.post("/api/v1/agents/register", json=payload)
    second = client.post("/api/v1/agents/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_invalid_agent_rejected(client):
    response = client.post(
        "/api/v1/agents/register",
        json={
            "name": "x",
            "description": "",
            "strategy_type": "momentum",
        },
    )

    assert response.status_code == 422



def test_list_agents(client):
    response = client.get("/api/v1/agents/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
