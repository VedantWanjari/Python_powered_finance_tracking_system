"""
tests/conftest.py
──────────────────
Pytest fixtures shared across all test modules.

Uses SQLite in-memory so no MySQL instance is required during tests.
Each test function gets a fresh database (via function-scoped db fixture).
"""

import datetime
import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction


@pytest.fixture(scope="session")
def app():
    """Create a test application with SQLite in-memory database."""
    flask_app = create_app("testing")
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SERVER_NAME": None,
        "RATELIMIT_ENABLED": False,
    })
    yield flask_app


@pytest.fixture(scope="session")
def db(app):
    """Create all tables once per test session."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def db_session(db, app):
    """
    Wrap each test in a transaction that is rolled back after the test.
    This keeps tests isolated without recreating the schema each time.
    """
    with app.app_context():
        # Remove all rows so each test starts with a clean slate
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
        yield _db


@pytest.fixture(scope="function")
def client(app, db_session):
    """Test client with a clean database for each test."""
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


# ── User fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture()
def sample_user(db_session, app):
    """A regular viewer-role user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="viewer")
        user.set_password("Test@1234")
        _db.session.add(user)
        _db.session.commit()
        # Re-fetch inside context so object is attached to the session
        return _db.session.get(User, user.id)


@pytest.fixture()
def sample_admin(db_session, app):
    """An admin-role user."""
    with app.app_context():
        user = User(username="adminuser", email="admin@example.com", role="admin")
        user.set_password("Admin@1234")
        _db.session.add(user)
        _db.session.commit()
        return _db.session.get(User, user.id)


@pytest.fixture()
def sample_analyst(db_session, app):
    """An analyst-role user."""
    with app.app_context():
        user = User(username="analyst", email="analyst@example.com", role="analyst")
        user.set_password("Analyst@1234")
        _db.session.add(user)
        _db.session.commit()
        return _db.session.get(User, user.id)


# ── Category fixture ──────────────────────────────────────────────────────────

@pytest.fixture()
def sample_category(db_session, app):
    """A default category for use in transaction tests."""
    with app.app_context():
        cat = Category(name="Food", color="#FF6B6B", is_default=True)
        _db.session.add(cat)
        _db.session.commit()
        return _db.session.get(Category, cat.id)


# ── Transaction fixtures ──────────────────────────────────────────────────────

@pytest.fixture()
def sample_transactions(db_session, sample_user, sample_category, app):
    """10 sample transactions for the sample_user. Returns list of simple dicts."""
    with app.app_context():
        today = datetime.date.today()
        ids = []
        for i in range(5):
            txn = Transaction(
                user_id=sample_user.id,
                amount=100 + i * 50,
                transaction_type="expense",
                category_id=sample_category.id,
                date=today.replace(day=max(1, i + 1)),
                description=f"Expense {i}",
            )
            _db.session.add(txn)
            _db.session.flush()   # assign id without committing
            ids.append({"id": txn.id, "user_id": sample_user.id})
        for i in range(5):
            txn = Transaction(
                user_id=sample_user.id,
                amount=500 + i * 100,
                transaction_type="income",
                category_id=None,
                date=today.replace(day=max(1, i + 1)),
                description=f"Income {i}",
            )
            _db.session.add(txn)
            _db.session.flush()
            ids.append({"id": txn.id, "user_id": sample_user.id})
        _db.session.commit()
        return ids   # return plain dicts so tests don't need a DB session


# ── Auth helpers ──────────────────────────────────────────────────────────────

def login(client, username: str, password: str):
    """Helper to log in and return the response."""
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
        content_type="application/json",
    )
