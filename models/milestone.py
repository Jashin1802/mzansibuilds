"""
models/milestone.py

Defines the Milestone model for MzansiBuilds.

Milestones are progress markers logged by a project owner to document
achievements and keep the community updated on their build journey.
"""

from __init__ import db
from datetime import datetime, timezone


class Milestone(db.Model):
    """
    Represents a single progress milestone on a project.

    Milestones are added by project owners to document meaningful
    achievements during the build process.

    Attributes:
        id (int): Primary key.
        project_id (int): Foreign key referencing the parent Project.
        text (str): Description of the milestone achieved.
        created_at (datetime): When this milestone was logged.
    """

    __tablename__ = "milestone"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Return a developer-friendly string representation of the milestone."""
        return f"<Milestone {self.text[:40]}>"
