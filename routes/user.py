from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import ProfileForm, TrekFilterForm
from models import db
from models.booking import Booking
from models.trek import Trek
from utils.decorators import user_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required
@user_required
def dashboard():
    open_treks = Trek.query.filter_by(status="Open").order_by(Trek.start_date).limit(6).all()
    my_bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "user/dashboard.html", open_treks=open_treks, my_bookings=my_bookings
    )


@user_bp.route("/treks")
@login_required
@user_required
def treks():
    form = TrekFilterForm(request.args)
    query = Trek.query.filter_by(status="Open")
    location = request.args.get("location", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    all_treks = query.order_by(Trek.start_date).all()
    return render_template("user/treks.html", treks=all_treks, form=form)


@user_bp.route("/treks/<int:trek_id>")
@login_required
@user_required
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    existing = Booking.query.filter_by(
        user_id=current_user.id, trek_id=trek.id, status="Booked"
    ).first()
    return render_template("user/trek_detail.html", trek=trek, existing_booking=existing)


@user_bp.route("/treks/<int:trek_id>/book", methods=["POST"])
@login_required
@user_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != "Open":
        flash("This trek is not open for booking.", "warning")
        return redirect(url_for("user.trek_detail", trek_id=trek.id))
    if trek.available_slots <= 0:
        flash("No slots available for this trek.", "danger")
        return redirect(url_for("user.trek_detail", trek_id=trek.id))
    existing = Booking.query.filter_by(
        user_id=current_user.id, trek_id=trek.id, status="Booked"
    ).first()
    if existing:
        flash("You already have an active booking for this trek.", "info")
        return redirect(url_for("user.trek_detail", trek_id=trek.id))

    booking = Booking(user_id=current_user.id, trek_id=trek.id, status="Booked")
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash(f"Successfully booked {trek.name}!", "success")
    return redirect(url_for("user.my_bookings"))


@user_bp.route("/bookings")
@login_required
@user_required
def my_bookings():
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )
    return render_template("user/bookings.html", bookings=bookings)


@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@user_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("user.my_bookings"))
    if booking.status != "Booked":
        flash("Only active bookings can be cancelled.", "warning")
        return redirect(url_for("user.my_bookings"))
    booking.status = "Cancelled"
    trek = booking.trek
    if trek.available_slots < trek.max_slots:
        trek.available_slots += 1
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("user.my_bookings"))


@user_bp.route("/history")
@login_required
@user_required
def history():
    completed = (
        Booking.query.filter_by(user_id=current_user.id, status="Completed")
        .order_by(Booking.booking_date.desc())
        .all()
    )
    cancelled = (
        Booking.query.filter_by(user_id=current_user.id, status="Cancelled")
        .order_by(Booking.booking_date.desc())
        .all()
    )
    return render_template("user/history.html", completed=completed, cancelled=cancelled)


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
@user_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("user.profile"))
    return render_template("user/profile.html", form=form)
