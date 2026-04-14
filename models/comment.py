"""
models/comment.py

Defines the Comment model for MzansiBuilds.

Comments allow any authenticated developer to engage with projects
in the live feed, ask questions, give feedback, or express support.
"""

from __init__ import db
from datetime import datetime, timezone


class Comment(db.Model):
    """
    Represents a comment posted on a project by a developer.

    Attributes:
        id (int): Primary key.
        project_id (int): Foreign key referencing the parent Project.
        user_id (int): Foreign key referencing the User who posted the comment.
        text (str): The comment content.
        created_at (datetime): When the comment was posted.
    """

    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Return a developer-friendly string representation of the comment."""
        return f"<Comment by user {self.user_id}>"
