from datetime import datetime

from models import db


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    contact = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(150))
    status = db.Column(
        db.String(20), default="pending", nullable=False
    )  # pending, approved, blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="staff_profile")

    @property
    def is_approved(self):
        return self.status == "approved"

    def __repr__(self):
        return f"<StaffProfile user_id={self.user_id} status={self.status}>"
