from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from models import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # admin, staff, user
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff_profile = db.relationship("StaffProfile", back_populates="user", uselist=False)
    bookings = db.relationship("Booking", back_populates="user", lazy="dynamic")
    assigned_treks = db.relationship("Trek", back_populates="assigned_staff", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_staff(self):
        return self.role == "staff"

    @property
    def is_trekker(self):
        return self.role == "user"

    def __repr__(self):
        return f"<User {self.email}>"
