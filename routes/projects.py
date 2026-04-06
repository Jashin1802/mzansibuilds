from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from __init__ import db
from models.project import Project, VALID_STAGES
from models.milestone import Milestone
from models.comment import Comment

SUPPORT_TYPES = ["Feedback", "Collaboration", "Code Review", "Design Help", "Testing", "Mentorship"]
TECH_TAGS = ["React", "Node.js", "Python", "Vue", "Django", "Go", "Rust",
             "Flutter", "Next.js", "TypeScript", "GraphQL", "PostgreSQL",
             "MongoDB", "AWS", "Docker"]

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        stage = request.form.get("stage", "Ideation")
        support = request.form.getlist("support")
        tags = request.form.getlist("tags")

        if not title:
            error = "Project title is required."
        elif stage not in VALID_STAGES:
            error = "Invalid stage selected."
        else:
            project = Project(
                user_id=current_user.id,
                title=title,
                description=description,
                stage=stage,
                support_needed=",".join(support),
                tech_tags=",".join(tags),
            )
            db.session.add(project)
            db.session.commit()
            flash(f'Project "{title}" created! 🚀', "success")
            return redirect(url_for("projects.view_project", project_id=project.id))

    return render_template(
        "projects/new.html",
        stages=VALID_STAGES,
        support_types=SUPPORT_TYPES,
        tech_tags=TECH_TAGS,
        error=error,
    )


@projects_bp.route("/projects/<int:project_id>")
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template(
        "projects/detail.html",
        project=project,
        stages=VALID_STAGES,
        support_types=SUPPORT_TYPES,
        tech_tags=TECH_TAGS,
    )


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        stage = request.form.get("stage", project.stage)
        support = request.form.getlist("support")
        tags = request.form.getlist("tags")

        if not title:
            error = "Project title is required."
        else:
            project.title = title
            project.description = description
            project.stage = stage
            project.support_needed = ",".join(support)
            project.tech_tags = ",".join(tags)
            db.session.commit()
            flash("Project updated! ✅", "success")
            return redirect(url_for("projects.view_project", project_id=project.id))

    return render_template(
        "projects/edit.html",
        project=project,
        stages=VALID_STAGES,
        support_types=SUPPORT_TYPES,
        tech_tags=TECH_TAGS,
        error=error,
    )


@projects_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("projects.my_projects"))


@projects_bp.route("/projects/<int:project_id>/milestone", methods=["POST"])
@login_required
def add_milestone(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    text = request.form.get("milestone_text", "").strip()
    if text:
        m = Milestone(project_id=project.id, text=text)
        db.session.add(m)
        db.session.commit()
        flash("Milestone logged! 🏁", "success")
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/projects/<int:project_id>/stage", methods=["POST"])
@login_required
def update_stage(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    new_stage = request.form.get("stage")
    if new_stage in VALID_STAGES:
        project.stage = new_stage
        db.session.commit()
        flash(f"Stage updated to {new_stage}! 📍", "success")
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/projects/<int:project_id>/complete", methods=["POST"])
@login_required
def complete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    project.is_completed = True
    db.session.commit()
    flash(f'🎉 Congratulations! "{project.title}" has been added to the Celebration Wall!', "success")
    return redirect(url_for("wall.wall"))


@projects_bp.route("/projects/<int:project_id>/comment", methods=["POST"])
@login_required
def add_comment(project_id):
    project = Project.query.get_or_404(project_id)
    text = request.form.get("comment_text", "").strip()
    if text:
        c = Comment(project_id=project.id, user_id=current_user.id, text=text)
        db.session.add(c)
        db.session.commit()
        flash("Comment posted! 💬", "success")
    return redirect(url_for("projects.view_project", project_id=project.id) + "#comments")


@projects_bp.route("/projects/<int:project_id>/collab", methods=["POST"])
@login_required
def toggle_collab(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id == current_user.id:
        flash("You cannot raise a hand on your own project.", "info")
        return redirect(url_for("projects.view_project", project_id=project.id))

    if project.has_raised_hand(current_user.id):
        project.lower_hand(current_user.id)
        flash("Hand lowered.", "info")
    else:
        project.raise_hand(current_user.id)
        flash("Hand raised! The project owner will be notified. 🙋", "success")

    db.session.commit()
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/my-projects")
@login_required
def my_projects():
    projects = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("projects/my_projects.html", projects=projects)
