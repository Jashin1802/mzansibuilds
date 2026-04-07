"""
test_routes_auth.py — Integration tests for authentication routes.

Tests cover registration, login, logout, and access control
to ensure unauthenticated users cannot access protected pages.
"""

from werkzeug.security import generate_password_hash
from models.user import User


class TestRegistration:
    """Tests for the /register route."""

    def test_register_page_loads(self, client):
        """The registration page returns a 200 status code."""
        response = client.get("/register")
        assert response.status_code == 200

    def test_successful_registration_creates_user(self, client, db):
        """A valid registration form creates a new user in the database."""
        client.post("/register", data={
            "name": "New Developer",
            "username": "new_dev",
            "bio": "Coding from Durban",
            "password": "securepass123",
            "confirm_password": "securepass123",
        })
        user = User.query.filter_by(username="new_dev").first()
        assert user is not None
        assert user.name == "New Developer"

    def test_registration_rejects_duplicate_username(self, client, db, sample_user):
        """Registration fails if the username is already taken."""
        response = client.post("/register", data={
            "name": "Another Dev",
            "username": sample_user.username,
            "password": "pass123456",
            "confirm_password": "pass123456",
        })
        assert b"already taken" in response.data

    def test_registration_rejects_mismatched_passwords(self, client, db):
        """Registration fails when password and confirm password do not match."""
        response = client.post("/register", data={
            "name": "Dev",
            "username": "dev_mismatch",
            "password": "password123",
            "confirm_password": "different123",
        })
        assert b"do not match" in response.data

    def test_registration_rejects_short_password(self, client, db):
        """Registration fails when the password is fewer than 6 characters."""
        response = client.post("/register", data={
            "name": "Dev",
            "username": "short_pass_dev",
            "password": "abc",
            "confirm_password": "abc",
        })
        assert b"6 characters" in response.data


class TestLogin:
    """Tests for the /login route."""

    def test_login_page_loads(self, client):
        """The login page returns a 200 status code."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_successful_login_redirects(self, client, db, sample_user):
        """A valid login redirects the user away from the login page."""
        response = client.post("/login", data={
            "username": "test_dev",
            "password": "testpassword123",
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_login_with_wrong_password_fails(self, client, db, sample_user):
        """Login with the wrong password shows an error message."""
        response = client.post("/login", data={
            "username": "test_dev",
            "password": "wrongpassword",
        })
        assert b"Incorrect password" in response.data

    def test_login_with_unknown_username_fails(self, client, db):
        """Login with a username that does not exist shows an error."""
        response = client.post("/login", data={
            "username": "ghost_user",
            "password": "somepassword",
        })
        assert b"not found" in response.data


class TestAccessControl:
    """Tests that protected routes redirect unauthenticated users."""

    def test_feed_requires_login(self, client):
        """The feed page redirects to login when not authenticated."""
        response = client.get("/feed", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_new_project_requires_login(self, client):
        """The new project page redirects to login when not authenticated."""
        response = client.get("/projects/new", follow_redirects=False)
        assert response.status_code == 302

    def test_wall_requires_login(self, client):
        """The celebration wall redirects to login when not authenticated."""
        response = client.get("/wall", follow_redirects=False)
        assert response.status_code == 302

    def test_profile_requires_login(self, client):
        """The profile page redirects to login when not authenticated."""
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302
