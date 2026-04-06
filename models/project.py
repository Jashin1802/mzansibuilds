from __init__ import db
from datetime import datetime, timezone

VALID_STAGES = ["Ideation", "Planning", "In Progress", "Testing", "Deployed"]

# Re-import the association table defined in user.py
from models.user import collab_hands


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(50), default="Ideation")
    support_needed = db.Column(db.String(300), default="")   # Comma-separated
    tech_tags = db.Column(db.String(300), default="")         # Comma-separated
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    milestones = db.relationship("Milestone", backref="project", lazy=True,
                                 cascade="all, delete-orphan", order_by="Milestone.created_at")
    comments = db.relationship("Comment", backref="project", lazy=True,
                               cascade="all, delete-orphan", order_by="Comment.created_at")
    collaborators = db.relationship("User", secondary=collab_hands, lazy="subquery",
                                    backref=db.backref("raised_hands", lazy=True))

    @property
    def tags_list(self):
        return [t.strip() for t in self.tech_tags.split(",") if t.strip()]

    @property
    def support_list(self):
        return [s.strip() for s in self.support_needed.split(",") if s.strip()]

    @property
    def stage_index(self):
        try:
            return VALID_STAGES.index(self.stage)
        except ValueError:
            return 0

    @property
    def progress_percent(self):
        return round(((self.stage_index + 1) / len(VALID_STAGES)) * 100)

    def raise_hand(self, user_id):
        from models.user import User
        user = User.query.get(user_id)
        if user and user not in self.collaborators:
            self.collaborators.append(user)

    def lower_hand(self, user_id):
        from models.user import User
        user = User.query.get(user_id)
        if user and user in self.collaborators:
            self.collaborators.remove(user)

    def has_raised_hand(self, user_id):
        return any(u.id == user_id for u in self.collaborators)

    def __repr__(self):
        return f"<Project {self.title}>"
