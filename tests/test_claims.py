from app.extensions import db
from tests.factories import CarFactory

def test_create_claim_success(client):
    car = CarFactory(); db.session.commit()
    payload = {"claimDate": "2024-05-10", "description": "Rear bumper", "amount": 450.00}
    resp = client.post(f"/api/cars/{car.id}/claims", json=payload)
    assert resp.status_code == 201
    assert "Location" in resp.headers
    data = resp.get_json()
    assert data["carId"] == car.id
    assert data["description"] == "Rear bumper"
    assert float(data["amount"]) == 450.0

def test_create_claim_missing_fields(client):
    car = CarFactory(); db.session.commit()
    resp = client.post(f"/api/cars/{car.id}/claims", json={"claimDate": "2024-01-01"})
    assert resp.status_code == 400

def test_create_claim_amount_invalid(client):
    car = CarFactory(); db.session.commit()
    payload = {"claimDate": "2024-01-01", "description": "x", "amount": -1}
    resp = client.post(f"/api/cars/{car.id}/claims", json=payload)
    assert resp.status_code == 400

def test_create_claim_404_car(client):
    resp = client.post("/api/cars/999/claims", json={"claimDate": "2024-01-01", "description":"x", "amount": 10})
    assert resp.status_code == 404
