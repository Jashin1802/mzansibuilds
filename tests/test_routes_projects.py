"""
test_routes_projects.py — Integration tests for project management routes.

Tests cover creating projects, adding milestones, commenting,
collaboration hand-raises, and ownership access control.
"""

from models.project import Project
from models.milestone import Milestone
from models.comment import Comment


class TestProjectCreation:
    """Tests for the /projects/new route."""

    def test_new_project_page_loads(self, logged_in_client):
        """The new project form loads successfully for a logged-in user."""
        response = logged_in_client.get("/projects/new")
        assert response.status_code == 200

    def test_valid_project_is_saved(self, logged_in_client, db, app):
        """Submitting a valid form creates a new project in the database."""
        logged_in_client.post("/projects/new", data={
            "title": "SA Weather App",
            "description": "Hyperlocal weather data for South Africa.",
            "stage": "Ideation",
            "support": ["Feedback"],
            "tags": ["Python"],
        }, follow_redirects=True)

        with app.app_context():
            project = Project.query.filter_by(title="SA Weather App").first()
            assert project is not None

    def test_empty_title_is_rejected(self, logged_in_client):
        """A project form with no title shows a validation error."""
        response = logged_in_client.post("/projects/new", data={
            "title": "",
            "description": "Some description.",
            "stage": "Ideation",
        })
        assert b"required" in response.data


class TestMilestones:
    """Tests for the milestone logging feature."""

    def test_owner_can_add_milestone(self, logged_in_client, db, sample_project, app):
        """The project owner can log a new milestone successfully."""
        logged_in_client.post(
            f"/projects/{sample_project.id}/milestone",
            data={"milestone_text": "First feature shipped!"},
            follow_redirects=True,
        )
        with app.app_context():
            milestone = Milestone.query.filter_by(text="First feature shipped!").first()
            assert milestone is not None

    def test_empty_milestone_is_not_saved(self, logged_in_client, db, sample_project, app):
        """An empty milestone text is not saved to the database."""
        logged_in_client.post(
            f"/projects/{sample_project.id}/milestone",
            data={"milestone_text": ""},
            follow_redirects=True,
        )
        with app.app_context():
            count = Milestone.query.filter_by(project_id=sample_project.id).count()
            assert count == 0


class TestComments:
    """Tests for the comment feature on project pages."""

    def test_logged_in_user_can_comment(self, logged_in_client, db, sample_project, app):
        """A logged-in user can post a comment on a project."""
        logged_in_client.post(
            f"/projects/{sample_project.id}/comment",
            data={"comment_text": "Great project idea!"},
            follow_redirects=True,
        )
        with app.app_context():
            comment = Comment.query.filter_by(text="Great project idea!").first()
            assert comment is not None

    def test_empty_comment_is_not_saved(self, logged_in_client, db, sample_project, app):
        """An empty comment is not saved to the database."""
        logged_in_client.post(
            f"/projects/{sample_project.id}/comment",
            data={"comment_text": ""},
            follow_redirects=True,
        )
        with app.app_context():
            count = Comment.query.filter_by(project_id=sample_project.id).count()
            assert count == 0


class TestAccessControl:
    """Tests that non-owners cannot modify other users' projects."""

    def test_non_owner_cannot_edit_project(self, logged_in_client, db, app, second_user):
        """A user cannot edit a project they do not own — expects 403."""
        from models.project import Project

        with app.app_context():
            other_project = Project(
                user_id=second_user.id,
                title="Other Dev Project",
                description="Not yours to edit.",
                stage="Ideation",
            )
            db.session.add(other_project)
            db.session.commit()
            project_id = other_project.id

        response = logged_in_client.post(
            f"/projects/{project_id}/edit",
            data={"title": "Hacked Title", "description": "x", "stage": "Ideation"},
        )
        assert response.status_code == 403

    def test_non_owner_cannot_delete_project(self, logged_in_client, db, app, second_user):
        """A user cannot delete a project they do not own — expects 403."""
        from models.project import Project

        with app.app_context():
            other_project = Project(
                user_id=second_user.id,
                title="Protected Project",
                description="Cannot be deleted by others.",
                stage="Planning",
            )
            db.session.add(other_project)
            db.session.commit()
            project_id = other_project.id

        response = logged_in_client.post(f"/projects/{project_id}/delete")
        assert response.status_code == 403
