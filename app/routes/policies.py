from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import InsurancePolicy, Car
from ..utils.dates import parse_iso_date, DateParseError

bp = Blueprint("policies", __name__, url_prefix="/api/cars")

def policy_to_dict(p: InsurancePolicy):
    return {
        "id": p.id,
        "carId": p.car_id,
        "provider": p.provider,
        "startDate": p.start_date.isoformat(),
        "endDate": p.end_date.isoformat(),
        "loggedExpiryAt": p.logged_expiry_at.isoformat() if p.logged_expiry_at else None,
    }

@bp.post("/<int:car_id>/policies")
def create_policy(car_id: int):
    # 404 dacă mașina nu există
    car = db.session.get(Car, car_id)
    if not car:
        return jsonify({"detail": "Car not found"}), 404

    data = request.get_json(silent=True) or {}
    provider = (data.get("provider") or "").strip() or None
    start_raw = data.get("startDate")
    end_raw = data.get("endDate")

    # validări: câmpuri obligatorii + format ISO + interval
    if not start_raw or not end_raw:
        return jsonify({"error": "startDate and endDate are required"}), 400

    try:
        start_date = parse_iso_date(start_raw)
        end_date = parse_iso_date(end_raw)
    except DateParseError as e:
        return jsonify({"error": str(e)}), 400

    if end_date < start_date:
        return jsonify({"error": "endDate must be greater than or equal to startDate"}), 400

    # (opțional) verificare viitoare pentru overlap de polițe active

    # ✅ creează polița și întoarce 201
    policy = InsurancePolicy(
        car_id=car_id,
        provider=provider,
        start_date=start_date,
        end_date=end_date,
    )
    db.session.add(policy)
    db.session.commit()

    return jsonify(policy_to_dict(policy)), 201

@bp.get("/<int:car_id>/policies")
def list_policies(car_id: int):
    car = db.session.get(Car, car_id)
    if not car:
        return jsonify({"detail": "Car not found"}), 404
    policies = (
        InsurancePolicy.query
        .filter_by(car_id=car_id)
        .order_by(InsurancePolicy.id)
        .all()
    )
    return jsonify([policy_to_dict(p) for p in policies])

@bp.get("/policies/<int:policy_id>")
def get_policy_by_id(policy_id: int):
    p = db.session.get(InsurancePolicy, policy_id)
    if not p:
        return jsonify({"detail": "Policy not found"}), 404
    return jsonify(policy_to_dict(p))
