"""
conftest.py — Shared pytest fixtures for MzansiBuilds test suite.

Sets up an isolated in-memory SQLite database for each test session
so tests never touch the real development database.
"""

import pytest
import sys
import os

# Make sure the app root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    """Create a test application instance with an in-memory database."""
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
        _db.create_all()


@pytest.fixture
def sample_user(db):
    """Create and return a sample registered user."""
    from models.user import User
    from werkzeug.security import generate_password_hash

    user = User(
        username="test_dev",
        name="Test Developer",
        bio="A test developer account",
        password_hash=generate_password_hash("testpassword123"),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(db):
    """Create and return a second sample user for collaboration tests."""
    from models.user import User
    from werkzeug.security import generate_password_hash

    user = User(
        username="second_dev",
        name="Second Developer",
        bio="Another test developer",
        password_hash=generate_password_hash("testpassword123"),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_project(db, sample_user):
    """Create and return a sample project owned by sample_user."""
    from models.project import Project

    project = Project(
        user_id=sample_user.id,
        title="Test Project",
        description="A project created for testing purposes.",
        stage="Ideation",
        support_needed="Feedback,Testing",
        tech_tags="Python,Flask",
    )
    db.session.add(project)
    db.session.commit()
    return project


@pytest.fixture
def logged_in_client(client, sample_user, app):
    """A test client with an active logged-in session."""
    with app.app_context():
        with client.session_transaction() as sess:
            sess["_user_id"] = str(sample_user.id)
            sess["_fresh"] = True
    return client
