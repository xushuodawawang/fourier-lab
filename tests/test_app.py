from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_index_renders() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Fourier Blue Lab" in response.text


def test_series_endpoint() -> None:
    response = client.get("/api/series", params={"terms": 4})
    data = response.json()
    assert response.status_code == 200
    assert len(data["x"]) == len(data["target"]) == len(data["approximation"])
    assert len(data["harmonics"]) == 4


def test_transition_endpoint() -> None:
    response = client.get("/api/transition", params={"period": 18})
    data = response.json()
    assert response.status_code == 200
    assert data["sample_count"] > 0
    assert len(data["omega"]) == len(data["envelope"])


def test_transform_endpoint() -> None:
    response = client.get("/api/transform", params={"signal": "sensor", "noise": 0.3, "cutoff": 2.0, "mode": "lowpass"})
    data = response.json()
    assert response.status_code == 200
    assert len(data["time_x"]) == len(data["clean"]) == len(data["filtered"])


def test_image_endpoint() -> None:
    response = client.get("/api/image-demo", params={"mode": "lowpass", "cutoff": 24})
    data = response.json()
    assert response.status_code == 200
    assert data["clean"].startswith("data:image/png;base64,")
