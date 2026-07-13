from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from config import Config
from models import db
from models.booking import Booking
from models.staff_profile import StaffProfile
from models.trek import Trek
from models.user import User


def seed_admin():
    admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=Config.ADMIN_EMAIL,
            name=Config.ADMIN_NAME,
            role="admin",
            password_hash=generate_password_hash(Config.ADMIN_PASSWORD),
        )
        db.session.add(admin)
        db.session.commit()


def seed_sample_data():
    if Trek.query.first():
        return

    admin = User.query.filter_by(role="admin").first()

    staff_users = []
    staff_data = [
        ("Rajesh Kumar", "rajesh@trek.com", "9876543210", 8, "Himalayan Treks"),
        ("Priya Sharma", "priya@trek.com", "9876543211", 5, "Western Ghats"),
        ("Amit Patel", "amit@trek.com", "9876543212", 10, "Desert & Adventure"),
    ]
    for name, email, phone, exp, spec in staff_data:
        user = User(
            email=email,
            name=name,
            role="staff",
            phone=phone,
            password_hash=generate_password_hash("staff123"),
        )
        db.session.add(user)
        db.session.flush()
        profile = StaffProfile(
            user_id=user.id,
            contact=phone,
            experience_years=exp,
            specialization=spec,
            status="approved",
        )
        db.session.add(profile)
        staff_users.append(user)

    trekker_data = [
        ("Ananya Reddy", "ananya@trek.com", "9123456780"),
        ("Vikram Singh", "vikram@trek.com", "9123456781"),
        ("Meera Iyer", "meera@trek.com", "9123456782"),
    ]
    trekkers = []
    for name, email, phone in trekker_data:
        user = User(
            email=email,
            name=name,
            role="user",
            phone=phone,
            password_hash=generate_password_hash("user123"),
        )
        db.session.add(user)
        trekkers.append(user)
    db.session.flush()

    today = date.today()
    treks_data = [
        {
            "name": "Kedarkantha Winter Trek",
            "location": "Uttarakhand",
            "difficulty": "Moderate",
            "duration_days": 6,
            "max_slots": 15,
            "available_slots": 12,
            "assigned_staff_id": staff_users[0].id,
            "status": "Open",
            "start_date": today + timedelta(days=30),
            "end_date": today + timedelta(days=35),
            "description": "A stunning winter trek in the Garhwal Himalayas with snow-covered trails and panoramic views of Swargarohini peaks.",
        },
        {
            "name": "Hampta Pass Crossing",
            "location": "Himachal Pradesh",
            "difficulty": "Hard",
            "duration_days": 5,
            "max_slots": 12,
            "available_slots": 8,
            "assigned_staff_id": staff_users[0].id,
            "status": "Open",
            "start_date": today + timedelta(days=45),
            "end_date": today + timedelta(days=49),
            "description": "Cross from lush Kullu valley to barren Lahaul — one of Himachal's most dramatic treks.",
        },
        {
            "name": "Kumara Parvatha",
            "location": "Karnataka",
            "difficulty": "Hard",
            "duration_days": 2,
            "max_slots": 20,
            "available_slots": 18,
            "assigned_staff_id": staff_users[1].id,
            "status": "Open",
            "start_date": today + timedelta(days=20),
            "end_date": today + timedelta(days=21),
            "description": "The highest peak in Pushpagiri Wildlife Sanctuary, popular among Bangalore trekkers.",
        },
        {
            "name": "Rajmachi Fort Trek",
            "location": "Maharashtra",
            "difficulty": "Easy",
            "duration_days": 1,
            "max_slots": 25,
            "available_slots": 20,
            "assigned_staff_id": staff_users[1].id,
            "status": "Open",
            "start_date": today + timedelta(days=14),
            "end_date": today + timedelta(days=14),
            "description": "A beginner-friendly monsoon trek near Lonavala with historic forts and waterfalls.",
        },
        {
            "name": "Sandakphu - Phalut Trek",
            "location": "West Bengal",
            "difficulty": "Moderate",
            "duration_days": 7,
            "max_slots": 10,
            "available_slots": 10,
            "assigned_staff_id": staff_users[2].id,
            "status": "Approved",
            "start_date": today + timedelta(days=60),
            "end_date": today + timedelta(days=66),
            "description": "Walk along the Singalila Ridge with views of Kanchenjunga, Everest, Lhotse, and Makalu.",
        },
        {
            "name": "Valley of Flowers",
            "location": "Uttarakhand",
            "difficulty": "Easy",
            "duration_days": 4,
            "max_slots": 18,
            "available_slots": 0,
            "assigned_staff_id": staff_users[0].id,
            "status": "Completed",
            "start_date": today - timedelta(days=30),
            "end_date": today - timedelta(days=26),
            "description": "UNESCO World Heritage site blooming with alpine flowers — a monsoon classic.",
        },
    ]

    trek_objects = []
    for data in treks_data:
        trek = Trek(**data)
        db.session.add(trek)
        trek_objects.append(trek)
    db.session.flush()

    bookings = [
        (trekkers[0].id, trek_objects[0].id, "Booked"),
        (trekkers[1].id, trek_objects[0].id, "Booked"),
        (trekkers[2].id, trek_objects[0].id, "Booked"),
        (trekkers[0].id, trek_objects[2].id, "Booked"),
        (trekkers[1].id, trek_objects[2].id, "Booked"),
        (trekkers[0].id, trek_objects[5].id, "Completed"),
        (trekkers[1].id, trek_objects[5].id, "Completed"),
    ]
    for user_id, trek_id, status in bookings:
        db.session.add(Booking(user_id=user_id, trek_id=trek_id, status=status))

    pending_staff = User(
        email="pending.staff@trek.com",
        name="Suresh Nair",
        role="staff",
        phone="9988776655",
        password_hash=generate_password_hash("staff123"),
    )
    db.session.add(pending_staff)
    db.session.flush()
    db.session.add(
        StaffProfile(
            user_id=pending_staff.id,
            contact="9988776655",
            experience_years=3,
            specialization="Coastal Treks",
            status="pending",
        )
    )

    db.session.commit()
