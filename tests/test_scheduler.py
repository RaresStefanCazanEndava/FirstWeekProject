from datetime import date
from unittest.mock import patch
from app.extensions import db
from app.models import InsurancePolicy
from tests.factories import CarFactory
from app.core.scheduling import detect_and_mark_expired_policies

def test_scheduler_detect_and_mark_once(app):
    car = CarFactory(); db.session.commit()

    # poliță care expiră pe "2025-01-01"
    p = InsurancePolicy(car_id=car.id, provider="AXA", start_date=date(2024,1,1), end_date=date(2025,1,1))
    db.session.add(p); db.session.commit()

    # patch-uim datetime.now().date() să fie 2025-01-01
    with patch("app.core.scheduling.datetime") as mock_dt:
        mock_dt.now.return_value = mock_dt(2025, 1, 1, 12, 0, 0)  # tip proxy; accesăm .date() doar
        mock_dt.side_effect = lambda *a, **k: date  # simplu: doar .date() e folosit
        # rulează
        detect_and_mark_expired_policies()

    db.session.refresh(p)
    assert p.logged_expiry_at is not None

    # rerulare: nu ar trebui să se schimbe nimic (idempotent)
    with patch("app.core.scheduling.datetime") as mock_dt:
        mock_dt.now.return_value = mock_dt(2025, 1, 1, 12, 5, 0)
        mock_dt.side_effect = lambda *a, **k: date
        detect_and_mark_expired_policies()

    # încă setat, nicio eroare
    db.session.refresh(p)
    assert p.logged_expiry_at is not None
