"""Root fixtures for the api/flask_app test suite.

Two import-time hazards drive the ordering of this file (see test.md at the
repo root for the full write-up):

1. `api.flask_app.app` runs `Config.validate_config()` and `db.create_all()`
   at module import time (`app = create_app()` executes as soon as the module
   is imported, not lazily). So required env vars and a reachable
   SQLALCHEMY_DATABASE_URI must exist *before* anything imports that module —
   including other test files' own module-level imports, which pytest
   resolves during collection, before any fixture runs. Hence all of this is
   plain module-level code, not fixture bodies.
2. `api/` has no `__init__.py` (namespace package), so `import api.flask_app`
   needs the repo root on sys.path — not guaranteed by default depending on
   how/where pytest is invoked.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers import (  # noqa: E402
    TEST_CHANNEL_ACCESS_TOKEN,
    TEST_CHANNEL_SECRET,
    TEST_EXAM_API_URL,
    TEST_FRONTEND_URL,
    TEST_LINE_LOGIN_CHANNEL_ID,
    TEST_LINE_LOGIN_CHANNEL_SECRET,
    TEST_LINE_LOGIN_REDIRECT_URI,
    TEST_OPENAI_API_KEY,
)

# File-backed SQLite, not sqlite:///:memory: — Flask-SQLAlchemy's connection
# pool can open more than one physical connection, and each connection to
# :memory: is its own separate empty database. A temp file is shared
# correctly across connections with zero source changes.
_TMP_DIR = tempfile.mkdtemp(prefix="lawbot_test_db_")
_TEST_DB_PATH = os.path.join(_TMP_DIR, "test.db")

# Force-override (not setdefault) every one of these: docker-compose's "api"
# service declares `env_file: .env`, so `docker compose run api ...` loads
# the real, ambient .env secrets into the container BEFORE this file runs.
# setdefault() would then keep those real values instead of our test
# constants — e.g. compute_line_signature() (helpers.py) hardcodes
# TEST_CHANNEL_SECRET, so if the app ends up validating against the real
# CHANNEL_SECRET instead, every signature-based test silently breaks. Tests
# must be 100% reproducible regardless of ambient environment (docker
# compose, a developer's shell, CI), so every var the app reads is pinned
# here unconditionally.
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ["CHANNEL_SECRET"] = TEST_CHANNEL_SECRET
os.environ["CHANNEL_ACCESS_TOKEN"] = TEST_CHANNEL_ACCESS_TOKEN
os.environ["OPENAI_API_KEY"] = TEST_OPENAI_API_KEY
os.environ["LINE_LOGIN_CHANNEL_ID"] = TEST_LINE_LOGIN_CHANNEL_ID
os.environ["LINE_LOGIN_CHANNEL_SECRET"] = TEST_LINE_LOGIN_CHANNEL_SECRET
os.environ["LINE_LOGIN_REDIRECT_URI"] = TEST_LINE_LOGIN_REDIRECT_URI
os.environ["FRONTEND_URL"] = TEST_FRONTEND_URL
os.environ["EXAM_API_URL"] = TEST_EXAM_API_URL
os.environ["CORS_ORIGINS"] = "*"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest  # noqa: E402

from api.flask_app.app import app as _flask_app  # noqa: E402
from api.flask_app.models import db as _db  # noqa: E402
from api.flask_app.models import User  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _test_db_dir_cleanup():
    yield
    shutil.rmtree(_TMP_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def app():
    """The single Flask app instance, shared across the whole test session."""
    _flask_app.config.update(TESTING=True)
    with _flask_app.app_context():
        _db.create_all()
    yield _flask_app


@pytest.fixture
def client(app):
    """Function-scoped, not session-scoped: Flask's test client keeps a
    cookie jar across requests, so a session-scoped client would leak
    logged-in session cookies (set via session_transaction() in
    logged_in_client) into unrelated tests that request a plain client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def _clean_db(app):
    """Wipe all rows after every test so each test starts from an empty DB."""
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def app_context(app):
    """An active app context, for tests that need `current_app`/`db.session`
    without going through a real request (e.g. core.security, model tests)."""
    with app.app_context():
        yield app


@pytest.fixture
def db_session(app_context):
    return _db.session


@pytest.fixture
def make_user(app_context):
    """Factory fixture: seed a User row, return its id."""
    def _make(user_id="Utestuser0001"):
        if not User.exists(user_id):
            User.create(user_id)
        return user_id
    return _make


@pytest.fixture
def logged_in_client(client, make_user):
    """A test client whose session already has a logged-in user_id, bypassing
    the real LINE OAuth flow."""
    user_id = make_user()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["display_name"] = "Test User"
    yield client
