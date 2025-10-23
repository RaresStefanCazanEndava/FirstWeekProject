from flask import Blueprint, jsonify
from ..services.history_service import get_history, car_exists

bp = Blueprint("history", __name__, url_prefix="/api/cars")

@bp.get("/<int:car_id>/history")
def car_history(car_id: int):
    if not car_exists(car_id):
        return jsonify({"detail": "Car not found"}), 404
    events = get_history(car_id)
    return jsonify(events)
