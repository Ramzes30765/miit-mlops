from fastapi.testclient import TestClient
import pytest

from app.api.v2 import items, users
from app.main import app as basic_app
from app.main_v1 import app as v1_app
from app.main_v2 import app as v2_app
from app.main_v3 import app as v3_app


@pytest.fixture(autouse=True)
def clear_fake_databases():
    users.fake_users_db.clear()
    items.fake_items_db.clear()


def test_basic_routes_and_query_validation():
    client = TestClient(basic_app)

    assert client.get("/").json() == {"message": "Hello World"}
    assert client.get("/items/3").json() == {"item_id": 3}
    assert client.get("/search", params={"query": "model", "limit": 5}).json() == {
        "query": "model",
        "limit": 5,
    }
    assert client.get("/search", params={"query": "model", "limit": 0}).status_code == 422
    assert client.get("/search", params={"query": "model"}).json()["limit"] == 10
    assert client.get("/search", params={"limit": 5}).status_code == 422


def test_v1_routes_use_v1_prefix():
    client = TestClient(v1_app)

    assert client.get("/api/v1/users").status_code == 200
    assert client.get("/api/v1/items").status_code == 200
    assert client.get("/users").status_code == 404


def test_v2_creates_user_without_returning_password():
    client = TestClient(v2_app)
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret1",
    }

    response = client.post("/api/v2/users", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "items": [],
    }
    assert "password" not in response.json()


def test_v2_rejects_invalid_email():
    client = TestClient(v2_app)

    response = client.post(
        "/api/v2/users",
        json={"name": "Alice", "email": "invalid", "password": "secret1"},
    )

    assert response.status_code == 422


def test_v2_rejects_short_password():
    client = TestClient(v2_app)

    response = client.post(
        "/api/v2/users",
        json={"name": "Alice", "email": "alice@example.com", "password": "123"},
    )

    assert response.status_code == 422


def test_v2_returns_404_for_missing_user():
    client = TestClient(v2_app)

    response = client.get("/api/v2/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_v2_creates_and_lists_items():
    client = TestClient(v2_app)
    client.post(
        "/api/v2/users",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret1"},
    )
    payload = {"title": "Model card", "description": "Version 1", "owner_id": 1}

    created = client.post("/api/v2/items", json=payload)
    listed = client.get("/api/v2/items")
    owner = client.get("/api/v2/users/1")

    assert created.status_code == 201
    assert created.json() == {"id": 1, **payload}
    assert listed.json() == [{"id": 1, **payload}]
    assert owner.json()["items"] == [{"id": 1, **payload}]


def test_v2_returns_404_for_missing_item_owner():
    client = TestClient(v2_app)

    response = client.post(
        "/api/v2/items",
        json={"title": "Model card", "owner_id": 999},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Owner not found"}


@pytest.mark.parametrize("app", [basic_app, v1_app, v2_app, v3_app])
def test_documentation_is_available(app):
    client = TestClient(app)

    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_v3_health_and_text_prediction():
    client = TestClient(v3_app)

    health = client.get("/health")
    prediction = client.post("/api/v3/predict-text", json={"prompt": "Привет"})

    assert health.json() == {"status": "ok", "model_version": "demo-llm-v1"}
    assert prediction.status_code == 200
    assert prediction.json()["reply"] == "Модель отвечает на запрос: Привет"
    assert prediction.json()["model_version"] == "demo-llm-v1"
    assert prediction.json()["latency_ms"] >= 0
    assert client.post("/api/v3/predict-text", json={"prompt": ""}).status_code == 422
    assert client.post("/api/v2/predict-text", json={"prompt": "Привет"}).status_code == 404
