from flask import Blueprint, jsonify
from sqlalchemy import text
from ..extensions import db

bp = Blueprint("health", __name__, url_prefix="/health")

@bp.get("")
def health():
    return jsonify(status="ok")

@bp.get("/db")
def health_db():
    # “Ping” simplu la DB
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(database="up")
    except Exception as e:
        return jsonify(database="down", error=str(e)), 500
    
@bp.get("/db-url")
def db_url():
    from flask import current_app, jsonify
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    # maschează user:parola doar ca să nu le logăm
    safe = uri.replace("postgres:postgres@", "****:****@")
    return jsonify(sqlalchemy_database_uri=safe)

@bp.get("/scheduler")
def scheduler_status():
    from ..core.scheduling import _scheduler
    if not _scheduler or not _scheduler.running:
        return {"enabled": False, "running": False}
    jobs = []
    for j in _scheduler.get_jobs():
        jobs.append({
            "id": j.id,
            "nextRunTime": j.next_run_time.isoformat() if j.next_run_time else None
        })
    return {"enabled": True, "running": True, "jobs": jobs}

