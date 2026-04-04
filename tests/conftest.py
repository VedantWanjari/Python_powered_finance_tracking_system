import datetime
import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction

@pytest.fixture(scope="session")
def app():
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
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope="function")
def db_session(db, app):
    with app.app_context():
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
        yield _db

@pytest.fixture(scope="function")
def client(app, db_session):
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture()
def sample_user(db_session, app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="viewer")
        user.set_password("Test@1234")
        _db.session.add(user)
        _db.session.commit()
        return _db.session.get(User, user.id)

@pytest.fixture()
def sample_admin(db_session, app):
    with app.app_context():
        user = User(username="adminuser", email="admin@example.com", role="admin")
        user.set_password("Admin@1234")
        _db.session.add(user)
        _db.session.commit()
        return _db.session.get(User, user.id)

@pytest.fixture()
def sample_analyst(db_session, app):
    with app.app_context():
        user = User(username="analyst", email="analyst@example.com", role="analyst")
        user.set_password("Analyst@1234")
        _db.session.add(user)
        _db.session.commit()
        return _db.session.get(User, user.id)

@pytest.fixture()
def sample_category(db_session, app):
    with app.app_context():
        cat = Category(name="Food", color="#FF6B6B", is_default=True)
        _db.session.add(cat)
        _db.session.commit()
        return _db.session.get(Category, cat.id)

@pytest.fixture()
def sample_transactions(db_session, sample_user, sample_category, app):
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
            _db.session.flush()
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
        return ids

def login(client, username: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
        content_type="application/json",
    )
