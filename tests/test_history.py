from datetime import date, timedelta
from decimal import Decimal
from app.extensions import db
from app.models import Claim, InsurancePolicy
from tests.factories import CarFactory

def test_history_ordering(client):
    car = CarFactory(); db.session.commit()

    # două polițe + un claim la mijloc
    p1 = InsurancePolicy(car_id=car.id, provider="A", start_date=date(2024,1,1), end_date=date(2024,12,31))
    p2 = InsurancePolicy(car_id=car.id, provider="B", start_date=date(2025,1,1), end_date=date(2025,12,31))
    c1 = Claim(car_id=car.id, claim_date=date(2024,5,10), description="Rear bumper", amount=Decimal("450.00"))
    db.session.add_all([p1, p2, c1]); db.session.commit()

    resp = client.get(f"/api/cars/{car.id}/history")
    assert resp.status_code == 200
    events = resp.get_json()
    # ordinea: p1 (2024-01-01), c1 (2024-05-10), p2 (2025-01-01)
    assert events[0]["type"] == "POLICY" and events[0]["policyId"] == p1.id
    assert events[1]["type"] == "CLAIM"  and events[1]["claimId"]  == c1.id
    assert events[2]["type"] == "POLICY" and events[2]["policyId"] == p2.id
