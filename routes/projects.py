"""
routes/projects.py

Project management routes for MzansiBuilds.

Handles the full lifecycle of a project: creation, editing, stage updates,
milestone logging, commenting, collaboration hand-raises, completion,
and deletion. All routes require authentication. Mutation routes enforce
ownership — only the project owner can modify their own projects.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from __init__ import db
from models.project import Project, VALID_STAGES
from models.milestone import Milestone
from models.comment import Comment

SUPPORT_TYPES = ["Feedback", "Collaboration", "Code Review", "Design Help", "Testing", "Mentorship"]
TECH_TAGS = [
    "React", "Node.js", "Python", "Vue", "Django", "Go", "Rust",
    "Flutter", "Next.js", "TypeScript", "GraphQL", "PostgreSQL",
    "MongoDB", "AWS", "Docker"
]

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    """
    Create a new project entry.

    GET:  Render the new project form with stage and tag options.
    POST: Validate and save the new project, then redirect to its detail page.

    Args (form):
        title (str): Required. Project title.
        description (str): Required. Project description.
        stage (str): Must be one of VALID_STAGES.
        support (list): Zero or more support types from SUPPORT_TYPES.
        tags (list): Zero or more tech tags from TECH_TAGS.
    """
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
            flash(f'Project "{title}" created!', "success")
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
    """
    Display the detail page for a single project.

    Args:
        project_id (int): The primary key of the project to display.

    Returns:
        Rendered project detail template, or 404 if not found.
    """
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
    """
    Edit an existing project.

    Only the project owner can access this route.
    Non-owners receive HTTP 403 Forbidden.

    Args:
        project_id (int): The primary key of the project to edit.
    """
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
            flash("Project updated!", "success")
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
    """
    Permanently delete a project and all associated data.

    Only the project owner can delete their project.
    Non-owners receive HTTP 403 Forbidden.
    Cascades to milestones and comments via the ORM relationship config.

    Args:
        project_id (int): The primary key of the project to delete.
    """
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
    """
    Log a new milestone on a project.

    Only the project owner can log milestones.
    Empty milestone text is silently ignored.

    Args:
        project_id (int): The primary key of the project.

    Form args:
        milestone_text (str): Description of the milestone achieved.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    text = request.form.get("milestone_text", "").strip()
    if text:
        m = Milestone(project_id=project.id, text=text)
        db.session.add(m)
        db.session.commit()
        flash("Milestone logged!", "success")
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/projects/<int:project_id>/stage", methods=["POST"])
@login_required
def update_stage(project_id):
    """
    Update the development stage of a project.

    Only the project owner can update the stage.
    The new stage must be one of VALID_STAGES or it is ignored.

    Args:
        project_id (int): The primary key of the project.

    Form args:
        stage (str): The new stage value.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    new_stage = request.form.get("stage")
    if new_stage in VALID_STAGES:
        project.stage = new_stage
        db.session.commit()
        flash(f"Stage updated to {new_stage}!", "success")
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/projects/<int:project_id>/complete", methods=["POST"])
@login_required
def complete_project(project_id):
    """
    Mark a project as completed and add it to the Celebration Wall.

    Only the project owner can mark their project complete.
    Once marked complete, the project is excluded from the active feed
    and displayed on the Celebration Wall instead.

    Args:
        project_id (int): The primary key of the project.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    project.is_completed = True
    db.session.commit()
    flash(f'Congratulations! "{project.title}" has been added to the Celebration Wall!', "success")
    return redirect(url_for("wall.wall"))


@projects_bp.route("/projects/<int:project_id>/comment", methods=["POST"])
@login_required
def add_comment(project_id):
    """
    Post a comment on a project.

    Any authenticated developer can comment on any project.
    Empty comment text is silently ignored.

    Args:
        project_id (int): The primary key of the project being commented on.

    Form args:
        comment_text (str): The comment content.
    """
    project = Project.query.get_or_404(project_id)
    text = request.form.get("comment_text", "").strip()
    if text:
        c = Comment(project_id=project.id, user_id=current_user.id, text=text)
        db.session.add(c)
        db.session.commit()
        flash("Comment posted!", "success")
    return redirect(url_for("projects.view_project", project_id=project.id) + "#comments")


@projects_bp.route("/projects/<int:project_id>/collab", methods=["POST"])
@login_required
def toggle_collab(project_id):
    """
    Toggle a collaboration hand-raise on a project.

    If the current user has already raised their hand, this lowers it.
    If they have not, this raises it. Project owners cannot raise a hand
    on their own project.

    Args:
        project_id (int): The primary key of the project.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id == current_user.id:
        flash("You cannot raise a hand on your own project.", "info")
        return redirect(url_for("projects.view_project", project_id=project.id))

    if project.has_raised_hand(current_user.id):
        project.lower_hand(current_user.id)
        flash("Hand lowered.", "info")
    else:
        project.raise_hand(current_user.id)
        flash("Hand raised! The project owner will be notified.", "success")

    db.session.commit()
    return redirect(url_for("projects.view_project", project_id=project.id))


@projects_bp.route("/my-projects")
@login_required
def my_projects():
    """
    Display all projects belonging to the currently logged-in developer.

    Projects are ordered most recent first.
    """
    projects = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("projects/my_projects.html", projects=projects)
