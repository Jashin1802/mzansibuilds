from flask import Blueprint, render_template
from flask_login import login_required
from models.project import Project
from models.user import User

wall_bp = Blueprint("wall", __name__)


@wall_bp.route("/wall")
@login_required
def wall():
    completed = (
        Project.query.filter_by(is_completed=True)
        .order_by(Project.updated_at.desc())
        .all()
    )
    active_count = Project.query.filter_by(is_completed=False).count()
    return render_template("wall.html", completed_projects=completed, active_count=active_count)
