"""
Test di integrazione elementari per l'API LogiFast (criterio di accettazione:
"test di integrazione elementari che dimostrano l'esecuzione dell'API"). Usano il
test client di Flask: niente server di rete, ma il percorso completo route ->
validazione -> modello -> risposta JSON. Eseguire dalla cartella del progetto:

    pytest -q
"""
import sys
from pathlib import Path

import pytest

# Permette `from app import create_app` eseguendo pytest dalla cartella del PRJ.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def _valid_record(**override):
    record = {
        "pickup_location": "Milano",
        "delivery_location": "Roma",
        "pickup_datetime": "2026-07-01T09:30:00",
        "weight": 5.0,
        "service_type": "Express",
    }
    record.update(override)
    return record


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "OK"


def test_model_metadata(client):
    body = client.get("/model").get_json()
    assert body["model_version"]
    assert "pickup_datetime" in body["unused_fields"]
    assert "Milano" in body["known_locations"]


def test_predict_ok(client):
    body = client.post("/predict", json=_valid_record()).get_json()
    assert isinstance(body["predicted_delivery_time_hours"], float)
    assert body["reliability_score"] == 1.0
    assert body["warnings"] == []


def test_predict_missing_field(client):
    record = _valid_record()
    del record["weight"]
    response = client.post("/predict", json=record)
    assert response.status_code == 400
    assert "weight" in " ".join(response.get_json()["errors"])


def test_predict_invalid_service_type(client):
    response = client.post("/predict", json=_valid_record(service_type="Gold"))
    assert response.status_code == 400


def test_predict_unknown_city_warns(client):
    body = client.post("/predict", json=_valid_record(pickup_location="Zurigo")).get_json()
    assert body["reliability_score"] < 1.0
    assert any("Zurigo" in warning for warning in body["warnings"])


def test_predict_bad_body(client):
    response = client.post("/predict", data="non e' json", content_type="application/json")
    assert response.status_code == 400


def test_predict_batch_mixed(client):
    good = _valid_record()
    bad = _valid_record()
    del bad["service_type"]
    body = client.post("/predict/batch", json=[good, bad]).get_json()
    assert body["count"] == 2
    assert [item["status"] for item in body["results"]] == ["ok", "error"]
