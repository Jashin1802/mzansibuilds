from __init__ import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Association table for collaboration hand-raises
collab_hands = db.Table(
    "collab_hands",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(300), default="Developer building in public 🚀")
    password_hash = db.Column(db.String(255), nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    projects = db.relationship("Project", backref="author", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="commenter", lazy=True, cascade="all, delete-orphan")

    @property
    def avatar_initials(self):
        parts = self.name.split()
        return "".join(p[0].upper() for p in parts[:2])

    @property
    def project_count(self):
        return len(self.projects)

    @property
    def shipped_count(self):
        return sum(1 for p in self.projects if p.is_completed)

    @property
    def milestone_count(self):
        return sum(len(p.milestones) for p in self.projects)

    @property
    def collab_count(self):
        return sum(len(p.collaborators) for p in self.projects)

    def __repr__(self):
        return f"<User {self.username}>"
