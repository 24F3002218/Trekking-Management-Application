from flask import Blueprint, jsonify, request
from flask_login import login_required

from models.booking import Booking
from models.trek import Trek
from utils.decorators import admin_required, login_required_not_blacklisted

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/treks")
@login_required
@login_required_not_blacklisted
def list_treks():
    status = request.args.get("status")
    query = Trek.query
    if status:
        query = query.filter_by(status=status)
    treks = query.all()
    return jsonify(
        [
            {
                "id": t.id,
                "name": t.name,
                "location": t.location,
                "difficulty": t.difficulty,
                "duration_days": t.duration_days,
                "available_slots": t.available_slots,
                "max_slots": t.max_slots,
                "status": t.status,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "assigned_staff_id": t.assigned_staff_id,
            }
            for t in treks
        ]
    )


@api_bp.route("/treks/<int:trek_id>")
@login_required
@login_required_not_blacklisted
def get_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify(
        {
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots": trek.available_slots,
            "max_slots": trek.max_slots,
            "status": trek.status,
            "start_date": trek.start_date.isoformat(),
            "end_date": trek.end_date.isoformat(),
            "description": trek.description,
            "assigned_staff_id": trek.assigned_staff_id,
        }
    )


@api_bp.route("/bookings")
@login_required
@login_required_not_blacklisted
def list_bookings():
    from flask_login import current_user

    if current_user.is_admin:
        bookings = Booking.query.all()
    elif current_user.is_trekker:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
    elif current_user.is_staff:
        trek_ids = [
            t.id
            for t in Trek.query.filter_by(assigned_staff_id=current_user.id).all()
        ]
        bookings = Booking.query.filter(Booking.trek_id.in_(trek_ids)).all()
    else:
        bookings = []
    return jsonify(
        [
            {
                "id": b.id,
                "user_id": b.user_id,
                "trek_id": b.trek_id,
                "trek_name": b.trek.name,
                "booking_date": b.booking_date.isoformat(),
                "status": b.status,
            }
            for b in bookings
        ]
    )


@api_bp.route("/stats")
@login_required
@admin_required
def stats():
    from models.user import User

    return jsonify(
        {
            "total_treks": Trek.query.count(),
            "total_users": User.query.filter_by(role="user").count(),
            "total_staff": User.query.filter_by(role="staff").count(),
            "active_bookings": Booking.query.filter_by(status="Booked").count(),
            "completed_treks": Trek.query.filter_by(status="Completed").count(),
        }
    )
