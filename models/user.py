"""
models/user.py

Defines the User model for MzansiBuilds.

The User model represents a registered developer on the platform.
It integrates with Flask-Login for session management and exposes
computed properties used across templates and routes.
"""

from __init__ import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database by their ID.

    Required by Flask-Login to restore the current user from the session.

    Args:
        user_id (str): The user's primary key as a string.

    Returns:
        User: The matching User instance, or None if not found.
    """
    return User.query.get(int(user_id))


# Association table for collaboration hand-raises.
# Links users to projects they have expressed interest in collaborating on.
collab_hands = db.Table(
    "collab_hands",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    """
    Represents a registered developer on the MzansiBuilds platform.

    Attributes:
        id (int): Primary key.
        username (str): Unique handle used for login and public profile URLs.
        name (str): Full display name shown across the platform.
        bio (str): Short developer biography shown on the profile page.
        password_hash (str): PBKDF2-SHA256 hashed password - never plaintext.
        joined_at (datetime): Timestamp of when the account was created.
    """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(300), default="Developer building in public")
    password_hash = db.Column(db.String(255), nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    projects = db.relationship(
        "Project", backref="author", lazy=True, cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", backref="commenter", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def avatar_initials(self):
        """
        Generate avatar initials from the user's display name.

        Takes the first letter of each word in the name, up to two letters.

        Returns:
            str: One or two uppercase initials, e.g. 'SN' for 'Sipho Ndlovu'.
        """
        parts = self.name.split()
        return "".join(p[0].upper() for p in parts[:2])

    @property
    def project_count(self):
        """Return the total number of projects this user has created."""
        return len(self.projects)

    @property
    def shipped_count(self):
        """Return the number of projects this user has marked as completed."""
        return sum(1 for p in self.projects if p.is_completed)

    @property
    def milestone_count(self):
        """Return the total milestones logged across all of the user's projects."""
        return sum(len(p.milestones) for p in self.projects)

    @property
    def collab_count(self):
        """Return the total collaboration hand-raises received across all projects."""
        return sum(len(p.collaborators) for p in self.projects)

    def __repr__(self):
        """Return a developer-friendly string representation of the user."""
        return f"<User {self.username}>"
