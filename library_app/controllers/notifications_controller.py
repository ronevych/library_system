from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for

from library_app.services import notification_repository
from library_app.services.auth_service import admin_required
from library_app.services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.before_request
@admin_required
def ensure_admin():
    return None


@notifications_bp.get("/")
def list_notifications():
    # Автоматично перевіряємо всі оренди при відкритті сторінки
    NotificationService.bootstrap()
    NotificationService.check_all_rentals()
    notifications = notification_repository.all()
    return render_template("notifications.html", notifications=notifications)

