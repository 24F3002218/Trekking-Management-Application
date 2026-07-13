from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated


def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            abort(403)
        profile = current_user.staff_profile
        if not profile or profile.status != "approved":
            flash("Your staff account is not approved yet.", "warning")
            return redirect(url_for("auth.pending_approval"))
        if current_user.is_blacklisted:
            flash("Your account has been blacklisted.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)

    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_trekker:
            abort(403)
        if current_user.is_blacklisted:
            flash("Your account has been blacklisted.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)

    return decorated


def login_required_not_blacklisted(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_blacklisted:
            flash("Your account has been blacklisted.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)

    return decorated
