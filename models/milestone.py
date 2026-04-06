from __init__ import db
from datetime import datetime, timezone


class Milestone(db.Model):
    __tablename__ = "milestone"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Milestone {self.text[:40]}>"
