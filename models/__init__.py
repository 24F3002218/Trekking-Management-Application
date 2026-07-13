from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User  # noqa: E402, F401
from models.staff_profile import StaffProfile  # noqa: E402, F401
from models.trek import Trek  # noqa: E402, F401
from models.booking import Booking  # noqa: E402, F401
