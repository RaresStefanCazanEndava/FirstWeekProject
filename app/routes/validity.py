from flask import Blueprint, jsonify, request
from ..utils.dates import parse_iso_date, DateParseError
from ..services.validity_service import car_exists, is_insured_on

bp = Blueprint("validity", __name__, url_prefix="/api/cars")

@bp.get("/<int:car_id>/insurance-valid")
def insurance_valid(car_id: int):
    qdate = request.args.get("date")
    if not qdate:
        return jsonify({"error": "query param 'date' is required (YYYY-MM-DD)"}), 400

    try:
        d = parse_iso_date(qdate)
    except DateParseError as e:
        return jsonify({"error": str(e)}), 400

    if not car_exists(car_id):
        return jsonify({"detail": "Car not found"}), 404

    valid = is_insured_on(car_id, d)
    return jsonify({"carId": car_id, "date": d.isoformat(), "valid": bool(valid)})
