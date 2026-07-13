from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from forms import LoginForm, RegisterForm
from models import db
from models.staff_profile import StaffProfile
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        if current_user.is_staff:
            profile = current_user.staff_profile
            if profile and profile.status == "approved":
                return redirect(url_for("staff.dashboard"))
            return redirect(url_for("auth.pending_approval"))
        return redirect(url_for("user.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            if user.is_blacklisted:
                flash("Your account has been blacklisted. Contact admin.", "danger")
                return render_template("login.html", form=form)
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("auth.index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)

        user = User(
            email=email,
            name=form.name.data.strip(),
            role=form.role.data,
            phone=form.phone.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        if user.role == "staff":
            profile = StaffProfile(
                user_id=user.id,
                contact=form.contact.data or form.phone.data,
                experience_years=form.experience_years.data or 0,
                specialization=form.specialization.data,
                status="pending",
            )
            db.session.add(profile)
            db.session.commit()
            flash("Staff registration submitted. Await admin approval before login.", "info")
            return redirect(url_for("auth.login"))

        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/pending-approval")
@login_required
def pending_approval():
    if not current_user.is_staff:
        return redirect(url_for("auth.index"))
    profile = current_user.staff_profile
    if profile and profile.status == "approved":
        return redirect(url_for("staff.dashboard"))
    return render_template("pending_approval.html", profile=profile)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
