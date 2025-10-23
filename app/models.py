from .extensions import db
from sqlalchemy.sql import func


class Owner(db.Model):
    __tablename__ = "owner"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255))

    # relație 1-la-multe: un owner poate avea mai multe mașini
    cars = db.relationship("Car", back_populates="owner", cascade="all, delete")

    def __repr__(self):
        return f"<Owner {self.id} {self.name}>"

class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(64), unique=True, nullable=False)
    make = db.Column(db.String(64))
    model = db.Column(db.String(64))
    year_of_manufacture = db.Column(db.Integer)

    owner_id = db.Column(db.Integer, db.ForeignKey("owner.id"), nullable=False)
    owner = db.relationship("Owner", back_populates="cars")

    # relații cu celelalte entități
    policies = db.relationship("InsurancePolicy", back_populates="car", cascade="all, delete-orphan")
    claims = db.relationship("Claim", back_populates="car", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Car {self.vin} ({self.make} {self.model})>"

class InsurancePolicy(db.Model):
    __tablename__ = "insurance_policy"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    provider = db.Column(db.String(128))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    logged_expiry_at = db.Column(db.DateTime, nullable=True)

    car = db.relationship("Car", back_populates="policies")

    def __repr__(self):
        return f"<Policy {self.id} for Car {self.car_id}>"


class Claim(db.Model):
    __tablename__ = "claim"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    car = db.relationship("Car", back_populates="claims")

    def __repr__(self):
        return f"<Claim {self.id} for Car {self.car_id}>"
