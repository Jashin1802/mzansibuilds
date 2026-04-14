"""
models/project.py

Defines the Project model for MzansiBuilds.

A Project represents a software project that a developer is building
in public. It tracks the current stage, tech stack, support needed,
milestones, comments, and collaboration requests.
"""

from __init__ import db
from datetime import datetime, timezone

VALID_STAGES = ["Ideation", "Planning", "In Progress", "Testing", "Deployed"]

from models.user import collab_hands


class Project(db.Model):
    """
    Represents a software project shared publicly on MzansiBuilds.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing the owning User.
        title (str): Short project title displayed in the feed.
        description (str): Detailed description of the project.
        stage (str): Current development stage from VALID_STAGES.
        support_needed (str): Comma-separated list of support types requested.
        tech_tags (str): Comma-separated list of technologies used.
        is_completed (bool): True when the project has been marked as shipped.
        created_at (datetime): When the project entry was first created.
        updated_at (datetime): When the project was last modified.
    """

    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(50), default="Ideation")
    support_needed = db.Column(db.String(300), default="")
    tech_tags = db.Column(db.String(300), default="")
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    milestones = db.relationship(
        "Milestone", backref="project", lazy=True,
        cascade="all, delete-orphan", order_by="Milestone.created_at"
    )
    comments = db.relationship(
        "Comment", backref="project", lazy=True,
        cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    collaborators = db.relationship(
        "User", secondary=collab_hands, lazy="subquery",
        backref=db.backref("raised_hands", lazy=True)
    )

    @property
    def tags_list(self):
        """
        Parse the tech_tags string into a Python list.

        Returns:
            list[str]: Technology tags with whitespace stripped,
                       or an empty list if none are set.
        """
        return [t.strip() for t in self.tech_tags.split(",") if t.strip()]

    @property
    def support_list(self):
        """
        Parse the support_needed string into a Python list.

        Returns:
            list[str]: Support type strings, or an empty list if none are set.
        """
        return [s.strip() for s in self.support_needed.split(",") if s.strip()]

    @property
    def stage_index(self):
        """
        Return the zero-based index of the current stage in VALID_STAGES.

        Returns:
            int: Index from 0 (Ideation) to 4 (Deployed), defaults to 0.
        """
        try:
            return VALID_STAGES.index(self.stage)
        except ValueError:
            return 0

    @property
    def progress_percent(self):
        """
        Calculate the project's completion percentage based on its stage.

        Returns:
            int: A value from 20 (Ideation) to 100 (Deployed).
        """
        return round(((self.stage_index + 1) / len(VALID_STAGES)) * 100)

    def raise_hand(self, user_id):
        """
        Add a user to the project's collaborators list.

        If the user has already raised their hand, this method does nothing
        to prevent duplicate entries.

        Args:
            user_id (int): The ID of the user raising their hand.
        """
        from models.user import User
        user = User.query.get(user_id)
        if user and user not in self.collaborators:
            self.collaborators.append(user)

    def lower_hand(self, user_id):
        """
        Remove a user from the project's collaborators list.

        Args:
            user_id (int): The ID of the user lowering their hand.
        """
        from models.user import User
        user = User.query.get(user_id)
        if user and user in self.collaborators:
            self.collaborators.remove(user)

    def has_raised_hand(self, user_id):
        """
        Check whether a specific user has raised their hand on this project.

        Args:
            user_id (int): The ID of the user to check.

        Returns:
            bool: True if the user is in the collaborators list.
        """
        return any(u.id == user_id for u in self.collaborators)

    def __repr__(self):
        """Return a developer-friendly string representation of the project."""
        return f"<Project {self.title}>"
