from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import Car, Owner

bp = Blueprint("cars", __name__, url_prefix="/api/cars")

# funcție de conversie pentru răspuns JSON
def car_to_dict(c: Car):
    return {
        "id": c.id,
        "vin": c.vin,
        "make": c.make,
        "model": c.model,
        "yearOfManufacture": c.year_of_manufacture,
        "owner": {
            "id": c.owner.id,
            "name": c.owner.name,
            "email": c.owner.email,
        } if c.owner else None,
    }

# GET /api/cars  →  listă cu owner inclus
@bp.get("")
def list_cars():
    cars = Car.query.order_by(Car.id).all()
    return jsonify([car_to_dict(c) for c in cars])

# POST /api/cars  →  adaugă o mașină nouă
@bp.post("")
def create_car():
    data = request.get_json(silent=True) or {}
    vin = (data.get("vin") or "").strip()
    owner_id = data.get("ownerId")
    make = (data.get("make") or "").strip() or None
    model = (data.get("model") or "").strip() or None
    yom = data.get("yearOfManufacture")

    if not vin:
        return jsonify({"error": "vin is required"}), 400
    if not owner_id:
        return jsonify({"error": "ownerId is required"}), 400

    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({"error": f"Owner with id={owner_id} not found"}), 404

    car = Car(
        vin=vin,
        make=make,
        model=model,
        year_of_manufacture=yom,
        owner=owner
    )
    db.session.add(car)
    db.session.commit()

    return car_to_dict(car), 201
