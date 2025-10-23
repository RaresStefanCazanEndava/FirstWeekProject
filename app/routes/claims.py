from flask import Blueprint, jsonify, request, url_for, make_response
from ..extensions import db
from ..models import Car, Claim
from ..utils.dates import parse_iso_date, DateParseError
from ..utils.money import parse_amount, MoneyParseError

bp = Blueprint("claims", __name__, url_prefix="/api/cars")

def claim_to_dict(c: Claim):
    return {
        "id": c.id,
        "carId": c.car_id,
        "claimDate": c.claim_date.isoformat(),
        "description": c.description,
        "amount": float(c.amount),  # pt JSON simplu; poți folosi și str(c.amount)
        "createdAt": c.created_at.isoformat() if c.created_at else None,
    }

@bp.post("/<int:car_id>/claims")
def create_claim(car_id: int):
    # 404 dacă mașina nu există
    car = db.session.get(Car, car_id)
    if not car:
        return jsonify({"detail": "Car not found"}), 404

    data = request.get_json(silent=True) or {}
    claim_date_raw = data.get("claimDate")
    description = (data.get("description") or "").strip()
    amount_raw = data.get("amount")

    # câmpuri obligatorii
    if not claim_date_raw or not description or amount_raw is None:
        return jsonify({"error": "claimDate, description and amount are required"}), 400

    # validări
    try:
        claim_date = parse_iso_date(claim_date_raw)
    except DateParseError as e:
        return jsonify({"error": str(e)}), 400

    try:
        amount = parse_amount(amount_raw)
    except MoneyParseError as e:
        return jsonify({"error": str(e)}), 400

    claim = Claim(
        car_id=car_id,
        claim_date=claim_date,
        description=description,
        amount=amount,
    )
    db.session.add(claim)
    db.session.commit()

    location = url_for("claims.get_claim", car_id=car_id, claim_id=claim.id, _external=False)
    resp = make_response(claim_to_dict(claim), 201)
    resp.headers["Location"] = location
    return resp

@bp.get("/<int:car_id>/claims/<int:claim_id>")
def get_claim(car_id: int, claim_id: int):
    c = db.session.get(Claim, claim_id)
    if not c or c.car_id != car_id:
        return jsonify({"detail": "Claim not found"}), 404
    return claim_to_dict(c)

@bp.get("/<int:car_id>/claims")
def list_claims(car_id: int):
    # 404 dacă mașina nu există
    car = db.session.get(Car, car_id)
    if not car:
        return jsonify({"detail": "Car not found"}), 404

    claims = (
        Claim.query
        .filter(Claim.car_id == car_id)
        .order_by(Claim.claim_date.asc(), Claim.id.asc())
        .all()
    )
    return jsonify([claim_to_dict(c) for c in claims])
