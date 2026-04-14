"""
test_models_user.py — Unit tests for the User model.

Tests cover user creation, property methods, and
avatar initial generation logic.
"""

import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User


class TestUserCreation:
    """Tests for creating valid user instances."""

    def test_user_can_be_created(self, db):
        """A user can be added to the database with required fields."""
        user = User(
            username="jashin_dev",
            name="Jashin Developer",
            bio="Building cool things",
            password_hash=generate_password_hash("securepass"),
        )
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.filter_by(username="jashin_dev").first()
        assert retrieved is not None
        assert retrieved.name == "Jashin Developer"

    def test_username_must_be_unique(self, db, sample_user):
        """Two users cannot share the same username."""
        duplicate = User(
            username=sample_user.username,
            name="Duplicate User",
            password_hash=generate_password_hash("pass"),
        )
        db.session.add(duplicate)
        with pytest.raises(Exception):
            db.session.commit()

    def test_default_bio_is_set(self, db):
        """A user created without a bio gets the default bio text."""
        user = User(
            username="no_bio_dev",
            name="No Bio Dev",
            password_hash=generate_password_hash("pass"),
        )
        db.session.add(user)
        db.session.commit()
        assert user.bio == "Developer building in public"

    def test_joined_at_is_set_automatically(self, db, sample_user):
        """The joined_at timestamp is set on creation."""
        assert sample_user.joined_at is not None


class TestUserProperties:
    """Tests for computed properties on the User model."""

    def test_avatar_initials_two_names(self, sample_user):
        """Avatar initials are correctly derived from a two-part name."""
        sample_user.name = "Sipho Ndlovu"
        assert sample_user.avatar_initials == "SN"

    def test_avatar_initials_single_name(self, sample_user):
        """Avatar initials work when the user has only one name."""
        sample_user.name = "Sipho"
        assert sample_user.avatar_initials == "S"

    def test_avatar_initials_three_names(self, sample_user):
        """Only the first two initials are used for three-part names."""
        sample_user.name = "Amahle Bongi Dlamini"
        assert sample_user.avatar_initials == "AB"

    def test_project_count_starts_at_zero(self, db, sample_user):
        """A new user has zero projects."""
        assert sample_user.project_count == 0

    def test_project_count_increments(self, db, sample_user, sample_project):
        """Project count reflects the number of projects the user owns."""
        assert sample_user.project_count == 1

    def test_shipped_count_only_counts_completed(self, db, sample_user, sample_project):
        """Shipped count only includes completed projects."""
        assert sample_user.shipped_count == 0
        sample_project.is_completed = True
        db.session.commit()
        assert sample_user.shipped_count == 1

    def test_password_hash_is_not_plaintext(self, sample_user):
        """The stored password must not be the original plaintext string."""
        assert sample_user.password_hash != "testpassword123"

    def test_password_can_be_verified(self, sample_user):
        """The stored hash correctly verifies against the original password."""
        assert check_password_hash(sample_user.password_hash, "testpassword123")
