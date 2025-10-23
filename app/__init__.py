from flask import Flask
from .config import Config
from .extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Import models so Alembic sees metadata ---
    # (importul trebuie să fie după init_app şi în interiorul funcţiei)
    from . import models  # noqa: F401

    # --- Blueprints (importate în funcţie, evităm importuri circulare) ---
    from .routes.health import bp as health_bp
    from .routes.owners import bp as owners_bp
    from .routes.cars import bp as cars_bp
    from .routes.policies import bp as policies_bp
    from .routes.validity import bp as validity_bp
    from .routes.claims import bp as claims_bp
    from .routes.history import bp as history_bp

    # Ordinea nu contează, dar le grupăm logic
    for bp in (
        health_bp,
        owners_bp,
        cars_bp,
        policies_bp,
        validity_bp,
        claims_bp,
        history_bp,
    ):
        app.register_blueprint(bp)

    # --- APScheduler (după ce app-ul e complet inițializat) ---
    from .core.scheduling import init_scheduler
    init_scheduler(app)

    return app
