# ⬇️ SETEAZĂ ENV ÎNAINTE DE ORICE IMPORT DIN app
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SCHEDULER_ENABLED"] = "false"  # nu vrem APScheduler în testele unitare

import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    # (opțional) dublu asigurare:
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )
    with app.app_context():
        yield app

@pytest.fixture(autouse=True)
def _db_session(app):
    with app.app_context():
        _db.create_all()
        yield
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
