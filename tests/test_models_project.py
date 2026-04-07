"""
test_models_project.py — Unit tests for the Project model.

Tests cover project creation, stage progression, tag parsing,
progress calculation, and collaboration hand-raise logic.
"""

from models.project import Project, VALID_STAGES


class TestProjectCreation:
    """Tests for creating valid project instances."""

    def test_project_can_be_created(self, db, sample_user):
        """A project can be saved with all required fields."""
        project = Project(
            user_id=sample_user.id,
            title="My New Project",
            description="Building something great for SA.",
            stage="Ideation",
        )
        db.session.add(project)
        db.session.commit()

        retrieved = Project.query.filter_by(title="My New Project").first()
        assert retrieved is not None
        assert retrieved.description == "Building something great for SA."

    def test_project_defaults_to_not_completed(self, db, sample_project):
        """A newly created project is not completed by default."""
        assert sample_project.is_completed is False

    def test_created_at_is_set(self, db, sample_project):
        """The created_at timestamp is set on project creation."""
        assert sample_project.created_at is not None


class TestProjectTags:
    """Tests for tag and support list parsing."""

    def test_tags_list_parses_comma_separated_string(self, sample_project):
        """tech_tags string is correctly split into a Python list."""
        sample_project.tech_tags = "Python,Flask,PostgreSQL"
        assert sample_project.tags_list == ["Python", "Flask", "PostgreSQL"]

    def test_tags_list_empty_when_no_tags(self, sample_project):
        """An empty tech_tags string returns an empty list."""
        sample_project.tech_tags = ""
        assert sample_project.tags_list == []

    def test_support_list_parses_correctly(self, sample_project):
        """support_needed string is correctly split into a Python list."""
        sample_project.support_needed = "Feedback,Code Review"
        assert sample_project.support_list == ["Feedback", "Code Review"]

    def test_tags_list_strips_whitespace(self, sample_project):
        """Whitespace around tag names is stripped during parsing."""
        sample_project.tech_tags = "Python, Flask , Docker"
        assert sample_project.tags_list == ["Python", "Flask", "Docker"]


class TestProjectStageProgress:
    """Tests for stage index and progress percentage calculations."""

    def test_stage_index_ideation_is_zero(self, sample_project):
        """Ideation is the first stage, so its index should be 0."""
        sample_project.stage = "Ideation"
        assert sample_project.stage_index == 0

    def test_stage_index_deployed_is_last(self, sample_project):
        """Deployed is the last stage, so its index should be 4."""
        sample_project.stage = "Deployed"
        assert sample_project.stage_index == len(VALID_STAGES) - 1

    def test_progress_percent_ideation(self, sample_project):
        """A project at Ideation stage should show 20% progress."""
        sample_project.stage = "Ideation"
        assert sample_project.progress_percent == 20

    def test_progress_percent_deployed(self, sample_project):
        """A project at Deployed stage should show 100% progress."""
        sample_project.stage = "Deployed"
        assert sample_project.progress_percent == 100

    def test_all_stages_are_valid(self):
        """The VALID_STAGES list contains exactly the expected 5 stages."""
        assert VALID_STAGES == ["Ideation", "Planning", "In Progress", "Testing", "Deployed"]


class TestCollaboration:
    """Tests for the collaboration hand-raise feature."""

    def test_raise_hand_adds_user_to_collaborators(self, db, sample_project, second_user):
        """Raising a hand adds the user to the project's collaborators list."""
        sample_project.raise_hand(second_user.id)
        db.session.commit()
        assert sample_project.has_raised_hand(second_user.id) is True

    def test_lower_hand_removes_user_from_collaborators(self, db, sample_project, second_user):
        """Lowering a hand removes the user from the collaborators list."""
        sample_project.raise_hand(second_user.id)
        db.session.commit()
        sample_project.lower_hand(second_user.id)
        db.session.commit()
        assert sample_project.has_raised_hand(second_user.id) is False

    def test_raise_hand_is_idempotent(self, db, sample_project, second_user):
        """Raising a hand twice does not add the user to collaborators twice."""
        sample_project.raise_hand(second_user.id)
        sample_project.raise_hand(second_user.id)
        db.session.commit()
        count = sum(1 for u in sample_project.collaborators if u.id == second_user.id)
        assert count == 1

    def test_has_raised_hand_returns_false_for_non_collaborator(self, sample_project, sample_user):
        """has_raised_hand returns False for a user who has not raised their hand."""
        assert sample_project.has_raised_hand(sample_user.id) is False
