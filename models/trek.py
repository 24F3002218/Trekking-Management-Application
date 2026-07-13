from datetime import datetime

from models import db


class Trek(db.Model):
    __tablename__ = "treks"

    DIFFICULTIES = ["Easy", "Moderate", "Hard"]
    STATUSES = ["Pending", "Approved", "Open", "Closed", "Completed"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default="Moderate")
    duration_days = db.Column(db.Integer, nullable=False, default=1)
    max_slots = db.Column(db.Integer, nullable=False, default=10)
    available_slots = db.Column(db.Integer, nullable=False, default=10)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_staff = db.relationship("User", back_populates="assigned_treks")
    bookings = db.relationship(
        "Booking",
        back_populates="trek",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def booked_count(self):
        return self.bookings.filter_by(status="Booked").count()

    @property
    def is_open_for_booking(self):
        return self.status == "Open" and self.available_slots > 0

    def sync_available_slots(self):
        active = self.bookings.filter_by(status="Booked").count()
        self.available_slots = max(0, self.max_slots - active)

    def __repr__(self):
        return f"<Trek {self.name}>"
