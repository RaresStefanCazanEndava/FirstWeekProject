from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import Owner

bp = Blueprint("owners", __name__, url_prefix="/api/owners")

def owner_to_dict(o: Owner):
    return {"id": o.id, "name": o.name, "email": o.email}

@bp.get("")
def list_owners():
    owners = Owner.query.order_by(Owner.id).all()
    return jsonify([owner_to_dict(o) for o in owners])

@bp.post("")
def create_owner():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip() or None
    if not name:
        return jsonify({"error": "name is required"}), 400
    o = Owner(name=name, email=email)
    db.session.add(o)
    db.session.commit()
    return owner_to_dict(o), 201
