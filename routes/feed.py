from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.project import Project
from models.user import User

feed_bp = Blueprint("feed", __name__)


@feed_bp.route("/feed")
@login_required
def feed():
    active_projects = (
        Project.query.filter_by(is_completed=False)
        .order_by(Project.updated_at.desc())
        .all()
    )
    all_devs = User.query.order_by(User.joined_at.desc()).all()
    total_milestones = sum(len(p.milestones) for p in Project.query.all())
    completed_count = Project.query.filter_by(is_completed=True).count()

    stats = {
        "builders": User.query.count(),
        "active": len(active_projects),
        "shipped": completed_count,
        "milestones": total_milestones,
    }

    return render_template(
        "feed.html",
        projects=active_projects,
        devs=all_devs,
        stats=stats,
    )
