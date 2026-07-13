from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms import StaffTrekUpdateForm
from models import db
from models.booking import Booking
from models.trek import Trek
from utils.decorators import staff_required

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@login_required
@staff_required
def dashboard():
    assigned = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    trek_stats = []
    for trek in assigned:
        participant_count = trek.bookings.filter_by(status="Booked").count()
        trek_stats.append({"trek": trek, "participants": participant_count})
    return render_template("staff/dashboard.html", trek_stats=trek_stats)


@staff_bp.route("/treks")
@login_required
@staff_required
def treks():
    assigned = (
        Trek.query.filter_by(assigned_staff_id=current_user.id)
        .order_by(Trek.start_date.desc())
        .all()
    )
    return render_template("staff/treks.html", treks=assigned)


@staff_bp.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@login_required
@staff_required
def manage_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)

    form = StaffTrekUpdateForm(obj=trek)
    if form.validate_on_submit():
        if form.available_slots.data > trek.max_slots:
            flash("Available slots cannot exceed maximum slots.", "danger")
        else:
            booked = trek.bookings.filter_by(status="Booked").count()
            if form.available_slots.data < trek.max_slots - booked:
                flash(
                    f"Cannot set slots below booked count. {booked} slots are already booked.",
                    "danger",
                )
            else:
                trek.available_slots = form.available_slots.data
                trek.status = form.status.data
                db.session.commit()
                flash("Trek updated successfully.", "success")
                return redirect(url_for("staff.manage_trek", trek_id=trek.id))

    participants = (
        Booking.query.filter_by(trek_id=trek.id, status="Booked")
        .order_by(Booking.booking_date)
        .all()
    )
    return render_template(
        "staff/manage_trek.html", trek=trek, form=form, participants=participants
    )


@staff_bp.route("/treks/<int:trek_id>/start", methods=["POST"])
@login_required
@staff_required
def start_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
    if trek.status != "Open":
        flash("Only open treks can be marked as started.", "warning")
    else:
        trek.started_at = datetime.utcnow()
        trek.status = "Closed"
        flash("Trek marked as started. Status set to Closed.", "success")
        db.session.commit()
    return redirect(url_for("staff.manage_trek", trek_id=trek.id))


@staff_bp.route("/treks/<int:trek_id>/complete", methods=["POST"])
@login_required
@staff_required
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
    if trek.status not in ("Closed", "Open") or not trek.started_at:
        flash("Trek must be started before marking as completed.", "warning")
    else:
        trek.status = "Completed"
        trek.completed_at = datetime.utcnow()
        active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
        for booking in active_bookings:
            booking.status = "Completed"
        db.session.commit()
        flash("Trek marked as completed.", "success")
    return redirect(url_for("staff.manage_trek", trek_id=trek.id))
