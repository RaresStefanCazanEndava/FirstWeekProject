# app/core/scheduling.py
import os
import atexit
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import update, and_
from sqlalchemy.sql import func
from ..extensions import db
from ..models import InsurancePolicy

log = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None

def detect_and_mark_expired_policies():
    today = datetime.now().date()
    with db.session.begin():
        stmt = (update(InsurancePolicy)
                .where(and_(InsurancePolicy.end_date == today,
                            InsurancePolicy.logged_expiry_at.is_(None)))
                .values(logged_expiry_at=func.now())
                .returning(InsurancePolicy.id, InsurancePolicy.car_id, InsurancePolicy.end_date))
        rows = list(db.session.execute(stmt).all())
    for pid, car_id, end_date in rows:
        log.info(f"Policy {pid} for car {car_id} expired on {end_date}")

def init_scheduler(app):
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    if not app.config.get("SCHEDULER_ENABLED", False):
        app.logger.info("APScheduler disabled via config.")
        return None

    # Guard pentru reloader în dev: pornește DOAR în child
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        app.logger.info("Skipping APScheduler start in reloader parent process.")
        return None

    scheduler = BackgroundScheduler()
    interval_minutes = int(app.config.get("SCHEDULER_INTERVAL_MINUTES", 10))

    def _job_wrapper():
        with app.app_context():
            try:
                detect_and_mark_expired_policies()
            except Exception:
                app.logger.exception("Expiry job failed")

    scheduler.add_job(
        _job_wrapper,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="policy_expiry_job",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    app.logger.info(f"APScheduler started (interval={interval_minutes}m)")
    _scheduler = scheduler

    # Oprește doar la terminarea procesului
    atexit.register(lambda: scheduler.shutdown(wait=False))
    return scheduler
