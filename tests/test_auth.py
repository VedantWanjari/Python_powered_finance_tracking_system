import pytest
from tests.conftest import login

class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser", "email": "new@example.com", "password": "NewPass@1",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["data"]["username"] == "newuser"

    def test_register_duplicate_username(self, client, sample_user):
        resp = client.post("/api/auth/register", json={
            "username": "testuser", "email": "other@example.com", "password": "Other@1234",
        })
        assert resp.status_code == 409

    def test_register_invalid_email(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "user2", "email": "not-an-email", "password": "Valid@1234",
        })
        assert resp.status_code == 400

    def test_register_weak_password(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "user3", "email": "user3@example.com", "password": "weak",
        })
        assert resp.status_code == 400
        assert "errors" in resp.get_json()

class TestLogin:
    def test_login_success(self, client, sample_user):
        resp = login(client, "testuser", "Test@1234")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "success"

    def test_login_wrong_password(self, client, sample_user):
        resp = login(client, "testuser", "wrongpass")
        assert resp.status_code == 400

    def test_login_inactive_user(self, client, sample_user, app, db_session):
        with app.app_context():
            from app import db
            from app.models.user import User
            u = db.session.get(User, sample_user.id)
            u.is_active = False
            db.session.commit()
        resp = login(client, "testuser", "Test@1234")
        assert resp.status_code == 400

    def test_login_unknown_user(self, client):
        resp = login(client, "nobody", "Test@1234")
        assert resp.status_code == 400

class TestLogout:
    def test_logout(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        resp2 = client.get("/api/auth/me")
        assert resp2.status_code == 401

class TestGetMe:
    def test_get_me_authenticated(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["username"] == "testuser"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_update_me(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.put("/api/auth/me", json={"email": "updated@example.com"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["email"] == "updated@example.com"
