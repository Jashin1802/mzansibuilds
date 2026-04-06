from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "instance", "mzansibuilds.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access MzansiBuilds."
    login_manager.login_message_category = "info"

    # Register blueprints
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.feed import feed_bp
    from routes.wall import wall_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(wall_bp)
    app.register_blueprint(profile_bp)

    # Create tables
    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    """Seed demo data on first run."""
    from models.user import User
    from models.project import Project
    from models.milestone import Milestone
    from models.comment import Comment
    from werkzeug.security import generate_password_hash

    if User.query.first():
        return  # Already seeded

    # Create demo developers
    devs = [
        User(
            username="sipho_dev",
            name="Sipho Ndlovu",
            bio="Full-stack dev from Joburg. Building fintech for Africa 🌍",
            password_hash=generate_password_hash("password"),
        ),
        User(
            username="amahle_codes",
            name="Amahle Dlamini",
            bio="ML engineer passionate about NLP in African languages",
            password_hash=generate_password_hash("password"),
        ),
        User(
            username="kagiso_builds",
            name="Kagiso Sithole",
            bio="Mobile dev building apps for township entrepreneurs",
            password_hash=generate_password_hash("password"),
        ),
    ]
    for dev in devs:
        db.session.add(dev)
    db.session.flush()

    # Create demo projects
    p1 = Project(
        user_id=devs[0].id,
        title="PayFast Mini SDK",
        description="Lightweight payment SDK for South African startups — zero fees for the first 1000 transactions.",
        stage="In Progress",
        support_needed="Feedback,Testing",
        tech_tags="Node.js,TypeScript",
    )
    p2 = Project(
        user_id=devs[1].id,
        title="IsiZulu NLP Toolkit",
        description="Open-source NLP library for isiZulu language processing — tokenisation, sentiment, POS tagging.",
        stage="Testing",
        support_needed="Collaboration,Feedback",
        tech_tags="Python,TypeScript",
    )
    p3 = Project(
        user_id=devs[2].id,
        title="TuckShop POS",
        description="Offline-first POS app for township tuck shops. Works on cheap Android phones with no internet.",
        stage="Deployed",
        support_needed="",
        tech_tags="Flutter,PostgreSQL",
        is_completed=True,
    )
    for p in [p1, p2, p3]:
        db.session.add(p)
    db.session.flush()

    # Milestones
    milestones = [
        Milestone(project_id=p1.id, text="Core API wrapper done"),
        Milestone(project_id=p1.id, text="OAuth flow implemented"),
        Milestone(project_id=p2.id, text="Tokeniser v1 shipped"),
        Milestone(project_id=p2.id, text="Training dataset compiled (50k sentences)"),
        Milestone(project_id=p2.id, text="Sentiment model 78% accuracy"),
        Milestone(project_id=p3.id, text="Offline sync engine complete"),
        Milestone(project_id=p3.id, text="Beta tested with 12 tuck shops"),
        Milestone(project_id=p3.id, text="App Store approved!"),
        Milestone(project_id=p3.id, text="500 downloads in first week 🎉"),
    ]
    for m in milestones:
        db.session.add(m)

    # Comments
    comments = [
        Comment(
            project_id=p1.id,
            user_id=devs[1].id,
            text="This is exactly what we needed! Have you looked at Peach Payments too?",
        ),
        Comment(
            project_id=p2.id,
            user_id=devs[2].id,
            text="Would love to see Sesotho support! Raising hand for collab 🙋",
        ),
        Comment(
            project_id=p2.id,
            user_id=devs[0].id,
            text="Incredible work Amahle. Happy to help with the testing pipeline.",
        ),
        Comment(
            project_id=p3.id,
            user_id=devs[0].id,
            text="This is huge Kagiso! The offline-first approach is so important for SA townships.",
        ),
    ]
    for c in comments:
        db.session.add(c)

    # Collaboration hands raised
    p1.raise_hand(devs[1].id)
    p1.raise_hand(devs[2].id)
    p2.raise_hand(devs[0].id)
    p2.raise_hand(devs[2].id)

    db.session.commit()
