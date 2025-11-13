from __future__ import annotations

from flask import Blueprint, render_template

from library_app.services import notification_repository
from library_app.services.auth_service import admin_required

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.before_request
@admin_required
def ensure_admin():
    return None


@notifications_bp.get("/")
def list_notifications():
    notifications = notification_repository.all()
    return render_template("notifications.html", notifications=notifications)

