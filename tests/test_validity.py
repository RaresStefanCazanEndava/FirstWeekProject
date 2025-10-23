from datetime import date, timedelta
from app.extensions import db
from tests.factories import CarFactory, PolicyFactory

def test_validity_true(client):
    pol = PolicyFactory(
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=5)
    )
    db.session.commit()
    resp = client.get(f"/api/cars/{pol.car_id}/insurance-valid?date={date.today().isoformat()}")
    assert resp.status_code == 200
    assert resp.get_json()["valid"] is True

def test_validity_false(client):
    pol = PolicyFactory(
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() - timedelta(days=1)
    )
    db.session.commit()
    resp = client.get(f"/api/cars/{pol.car_id}/insurance-valid?date={date.today().isoformat()}")
    assert resp.status_code == 200
    assert resp.get_json()["valid"] is False

def test_validity_404_car(client):
    resp = client.get("/api/cars/999/insurance-valid?date=2025-01-01")
    assert resp.status_code == 404

def test_validity_400_bad_date(client):
    car = CarFactory(); db.session.commit()
    resp = client.get(f"/api/cars/{car.id}/insurance-valid?date=BAD")
    assert resp.status_code == 400
