from datetime import date, timedelta
from app.extensions import db
from tests.factories import CarFactory

def test_create_policy_success(client):
    car = CarFactory()
    db.session.commit()

    payload = {
        "provider": "AXA",
        "startDate": "2024-01-01",
        "endDate": "2024-12-31"
    }
    resp = client.post(f"/api/cars/{car.id}/policies", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["carId"] == car.id
    assert data["startDate"] == "2024-01-01"
    assert data["endDate"] == "2024-12-31"

def test_create_policy_404_car(client):
    resp = client.post("/api/cars/999/policies", json={"startDate":"2024-01-01","endDate":"2024-12-31"})
    assert resp.status_code == 404

def test_create_policy_end_before_start(client):
    car = CarFactory()
    db.session.commit()
    payload = {"startDate": "2024-06-01", "endDate": "2024-05-01"}
    resp = client.post(f"/api/cars/{car.id}/policies", json=payload)
    assert resp.status_code == 400
    assert "endDate must be greater" in resp.get_json()["error"]

def test_create_policy_bad_date_format(client):
    car = CarFactory(); db.session.commit()
    payload = {"startDate": "01-01-2024", "endDate": "2024/12/31"}
    resp = client.post(f"/api/cars/{car.id}/policies", json=payload)
    assert resp.status_code == 400
