"""
routes/auth.py

Authentication routes for MzansiBuilds.

Handles user registration, login, and logout. All routes in this
blueprint are publicly accessible — no login is required to reach them.
Successful authentication redirects users into the protected application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """
    Root route — redirect authenticated users to the feed,
    unauthenticated users to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("feed.feed"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle developer login.

    GET:  Render the login form.
    POST: Validate credentials. On success, redirect to the feed.
          On failure, re-render the form with an error message.

    Security:
        Uses check_password_hash for timing-attack resistant comparison.
        Never exposes whether a username exists or a password is wrong
        beyond the specific error messages shown.
    """
    if current_user.is_authenticated:
        return redirect(url_for("feed.feed"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()
        if not user:
            error = "Username not found."
        elif not check_password_hash(user.password_hash, password):
            error = "Incorrect password."
        else:
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("feed.feed"))

    return render_template("auth/login.html", error=error)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle new developer registration.

    GET:  Render the registration form.
    POST: Validate input, create user, log them in, redirect to the feed.

    Validation:
        - Name, username, and password are required
        - Password must be at least 6 characters
        - Password and confirm_password must match
        - Username must be unique across all users

    Security:
        Password is hashed with generate_password_hash before storage.
        The plaintext password is never persisted.
    """
    if current_user.is_authenticated:
        return redirect(url_for("feed.feed"))

    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip().replace(" ", "_")
        bio = request.form.get("bio", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not name or not username or not password:
            error = "Name, username and password are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif User.query.filter_by(username=username).first():
            error = "That username is already taken."
        else:
            user = User(
                name=name,
                username=username,
                bio=bio or "Developer building in public",
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Account created! Welcome to MzansiBuilds, {name}!", "success")
            return redirect(url_for("feed.feed"))

    return render_template("auth/register.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log the current user out and redirect to the login page.

    Requires an active login session — unauthenticated access
    is blocked by the @login_required decorator.
    """
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
