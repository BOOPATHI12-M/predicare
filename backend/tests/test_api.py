import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json()["status"] == "ok"


def test_simulation_and_measurements(client: TestClient) -> None:
    response = client.post("/api/measurements/simulate")
    assert response.status_code == 200
    assert response.json()["source"] == "simulation"
    assert client.get("/api/measurements").status_code == 200
