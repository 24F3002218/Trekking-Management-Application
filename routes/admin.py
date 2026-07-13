from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from forms import SearchForm, TrekForm
from models import db
from models.booking import Booking
from models.staff_profile import StaffProfile
from models.trek import Trek
from models.user import User
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_treks": Trek.query.count(),
        "total_users": User.query.filter_by(role="user").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_bookings": Booking.query.filter_by(status="Booked").count(),
    }
    recent_bookings = (
        Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    )
    return render_template(
        "admin/dashboard.html", stats=stats, recent_bookings=recent_bookings
    )


@admin_bp.route("/treks")
@login_required
@admin_required
def treks():
    search = request.args.get("q", "").strip()
    query = Trek.query
    if search:
        if search.isdigit():
            query = query.filter(
                or_(Trek.id == int(search), Trek.name.ilike(f"%{search}%"))
            )
        else:
            query = query.filter(
                or_(Trek.name.ilike(f"%{search}%"), Trek.location.ilike(f"%{search}%"))
            )
    all_treks = query.order_by(Trek.created_at.desc()).all()
    return render_template("admin/treks.html", treks=all_treks, search=search)


@admin_bp.route("/treks/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_trek():
    form = TrekForm()
    form.assigned_staff_id.choices = _staff_choices()
    if form.validate_on_submit():
        if form.end_date.data < form.start_date.data:
            flash("End date must be on or after start date.", "danger")
            return render_template("admin/trek_form.html", form=form, title="Add Trek")
        trek = Trek(
            name=form.name.data,
            location=form.location.data,
            difficulty=form.difficulty.data,
            duration_days=form.duration_days.data,
            max_slots=form.max_slots.data,
            available_slots=form.max_slots.data,
            assigned_staff_id=form.assigned_staff_id.data or None,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
        )
        db.session.add(trek)
        db.session.commit()
        flash("Trek created successfully.", "success")
        return redirect(url_for("admin.treks"))
    return render_template("admin/trek_form.html", form=form, title="Add Trek")


@admin_bp.route("/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    form = TrekForm(obj=trek)
    form.assigned_staff_id.choices = _staff_choices()
    if form.validate_on_submit():
        if form.end_date.data < form.start_date.data:
            flash("End date must be on or after start date.", "danger")
            return render_template(
                "admin/trek_form.html", form=form, title="Edit Trek", trek=trek
            )
        old_max = trek.max_slots
        trek.name = form.name.data
        trek.location = form.location.data
        trek.difficulty = form.difficulty.data
        trek.duration_days = form.duration_days.data
        trek.max_slots = form.max_slots.data
        trek.assigned_staff_id = form.assigned_staff_id.data or None
        trek.status = form.status.data
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data
        trek.description = form.description.data
        if form.max_slots.data != old_max:
            trek.sync_available_slots()
        db.session.commit()
        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.treks"))
    if request.method == "GET":
        form.assigned_staff_id.data = trek.assigned_staff_id or 0
    return render_template(
        "admin/trek_form.html", form=form, title="Edit Trek", trek=trek
    )


@admin_bp.route("/treks/<int:trek_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.", "success")
    return redirect(url_for("admin.treks"))


@admin_bp.route("/staff")
@login_required
@admin_required
def manage_staff():
    tab = request.args.get("tab", "pending")
    search = request.args.get("q", "").strip()
    query = StaffProfile.query.join(User)
    if tab == "pending":
        query = query.filter(StaffProfile.status == "pending")
    elif tab == "approved":
        query = query.filter(StaffProfile.status == "approved")
    elif tab == "blacklisted":
        query = query.filter(StaffProfile.status == "blacklisted")
    if search:
        if search.isdigit():
            query = query.filter(
                or_(User.id == int(search), User.name.ilike(f"%{search}%"))
            )
        else:
            query = query.filter(
                or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
            )
    profiles = query.order_by(StaffProfile.created_at.desc()).all()
    return render_template(
        "admin/staff.html", profiles=profiles, tab=tab, search=search
    )


@admin_bp.route("/staff/<int:profile_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_staff(profile_id):
    profile = StaffProfile.query.get_or_404(profile_id)
    profile.status = "approved"
    db.session.commit()
    flash(f"Staff {profile.user.name} approved.", "success")
    return redirect(url_for("admin.manage_staff", tab="approved"))


@admin_bp.route("/staff/<int:profile_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_staff(profile_id):
    profile = StaffProfile.query.get_or_404(profile_id)
    user = profile.user
    db.session.delete(profile)
    db.session.delete(user)
    db.session.commit()
    flash("Staff registration rejected and removed.", "info")
    return redirect(url_for("admin.manage_staff", tab="pending"))


@admin_bp.route("/staff/<int:profile_id>/blacklist", methods=["POST"])
@login_required
@admin_required
def blacklist_staff(profile_id):
    profile = StaffProfile.query.get_or_404(profile_id)
    profile.status = "blacklisted"
    profile.user.is_blacklisted = True
    db.session.commit()
    flash(f"Staff {profile.user.name} blacklisted.", "warning")
    return redirect(url_for("admin.manage_staff", tab="blacklisted"))


@admin_bp.route("/staff/<int:profile_id>/unblacklist", methods=["POST"])
@login_required
@admin_required
def unblacklist_staff(profile_id):
    profile = StaffProfile.query.get_or_404(profile_id)
    profile.status = "approved"
    profile.user.is_blacklisted = False
    db.session.commit()
    flash(f"Staff {profile.user.name} restored.", "success")
    return redirect(url_for("admin.manage_staff", tab="approved"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    search = request.args.get("q", "").strip()
    query = User.query.filter_by(role="user")
    if search:
        if search.isdigit():
            query = query.filter(or_(User.id == int(search), User.name.ilike(f"%{search}%")))
        else:
            query = query.filter(
                or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
            )
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users, search=search)


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@login_required
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f"User {user.name} blacklisted.", "warning")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/unblacklist", methods=["POST"])
@login_required
@admin_required
def unblacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f"User {user.name} restored.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template("admin/bookings.html", bookings=all_bookings)


@admin_bp.route("/history")
@login_required
@admin_required
def history():
    completed_treks = Trek.query.filter_by(status="Completed").order_by(
        Trek.completed_at.desc()
    ).all()
    completed_bookings = Booking.query.filter_by(status="Completed").order_by(
        Booking.booking_date.desc()
    ).all()
    return render_template(
        "admin/history.html",
        completed_treks=completed_treks,
        completed_bookings=completed_bookings,
    )


@admin_bp.route("/assign-staff/<int:trek_id>", methods=["POST"])
@login_required
@admin_required
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_id = request.form.get("staff_id", type=int)
    if staff_id:
        staff = User.query.filter_by(id=staff_id, role="staff").first()
        if staff and staff.staff_profile and staff.staff_profile.status == "approved":
            trek.assigned_staff_id = staff_id
            db.session.commit()
            flash(f"Staff assigned to {trek.name}.", "success")
        else:
            flash("Invalid staff selection.", "danger")
    return redirect(url_for("admin.treks"))


def _staff_choices():
    choices = [(0, "-- Unassigned --")]
    staff_list = (
        User.query.filter_by(role="staff")
        .join(StaffProfile)
        .filter(StaffProfile.status == "approved")
        .all()
    )
    choices.extend([(s.id, s.name) for s in staff_list])
    return choices
