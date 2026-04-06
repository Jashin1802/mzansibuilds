from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from __init__ import db
from models.user import User
from models.project import Project

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    return redirect(url_for("profile.view_profile", username=current_user.username))


@profile_bp.route("/profile/<username>")
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    projects = (
        Project.query.filter_by(user_id=user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("profile.html", user=user, projects=projects)


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "").strip()

        if not name:
            error = "Name is required."
        else:
            current_user.name = name
            current_user.bio = bio
            db.session.commit()
            flash("Profile updated! ✅", "success")
            return redirect(url_for("profile.profile"))

    return render_template("edit_profile.html", error=error)
