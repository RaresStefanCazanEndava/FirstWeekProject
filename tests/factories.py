import factory
from faker import Faker
from app.extensions import db
from app.models import Owner, Car, InsurancePolicy, Claim
from datetime import date, timedelta
from decimal import Decimal

fake = Faker()

class OwnerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Owner
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    name = factory.LazyAttribute(lambda _: fake.name())
    email = factory.LazyAttribute(lambda _: fake.email())

class CarFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Car
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    vin = factory.Sequence(lambda n: f"VIN-{n:06d}")
    make = "Test"
    model = "Car"
    year_of_manufacture = 2020
    owner = factory.SubFactory(OwnerFactory)

class PolicyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InsurancePolicy
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    car = factory.SubFactory(CarFactory)
    provider = "AXA"
    start_date = factory.LazyFunction(lambda: date.today() - timedelta(days=10))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=10))
    logged_expiry_at = None

class ClaimFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Claim
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    car = factory.SubFactory(CarFactory)
    claim_date = factory.LazyFunction(lambda: date.today())
    description = "Test claim"
    amount = Decimal("123.45")
