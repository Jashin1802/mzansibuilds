from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("feed.feed"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
            flash(f"Welcome back, {user.name}! 👋", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("feed.feed"))

    return render_template("auth/login.html", error=error)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
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
                bio=bio or "Developer building in public 🚀",
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Account created! Welcome to MzansiBuilds, {name}! 🎉", "success")
            return redirect(url_for("feed.feed"))

    return render_template("auth/register.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
