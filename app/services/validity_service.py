from datetime import date
from sqlalchemy import select
from ..extensions import db
from ..models import Car, InsurancePolicy

def car_exists(car_id: int) -> bool:
    return db.session.get(Car, car_id) is not None

def is_insured_on(car_id: int, d: date) -> bool:
    """True dacă există o poliță activă pentru data d (inclusiv capete)."""
    stmt = (
        select(InsurancePolicy.id)
        .where(InsurancePolicy.car_id == car_id)
        .where(InsurancePolicy.start_date <= d)
        .where(InsurancePolicy.end_date >= d)
        .limit(1)
    )
    return db.session.execute(stmt).first() is not None
