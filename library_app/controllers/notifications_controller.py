from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from library_app.models import db
from library_app.services import notification_repository, reader_repository
from library_app.services.auth_service import current_user, is_admin, is_authenticated, login_required
from library_app.services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.before_request
@login_required
def ensure_authenticated():
    return None


@notifications_bp.get("/")
def list_notifications():
    # Автоматично перевіряємо всі оренди при відкритті сторінки
    NotificationService.bootstrap()
    NotificationService.check_all_rentals()
    
    user = current_user()
    if user is None:
        return render_template("notifications.html", notifications=[], readers=[], user_is_admin=False)
    
    # Якщо адмін - показуємо всі сповіщення з можливістю фільтру
    if is_admin():
        reader_id_filter = request.args.get("reader_id", type=int)
        if reader_id_filter:
            notifications = notification_repository.for_reader(reader_id_filter)
        else:
            notifications = notification_repository.all()
        readers = reader_repository.all()
        return render_template("notifications.html", notifications=notifications, readers=readers, user_is_admin=True, selected_reader_id=reader_id_filter)
    
    # Якщо звичайний користувач - показуємо тільки його сповіщення
    if user.reader is None:
        return render_template("notifications.html", notifications=[], readers=[], user_is_admin=False)
    
    notifications = notification_repository.for_reader(user.reader.id)
    return render_template("notifications.html", notifications=notifications, readers=[], user_is_admin=False)


@notifications_bp.post("/<int:notification_id>/mark-read")
def mark_as_read(notification_id: int):
    """Позначає сповіщення як прочитане."""
    user = current_user()
    if user is None:
        return jsonify({"error": "Authentication required"}), 401
    
    notification = notification_repository.get(notification_id)
    if notification is None:
        return jsonify({"error": "Notification not found"}), 404
    
    # Перевіряємо, чи користувач має право читати це сповіщення
    if not is_admin() and (user.reader is None or notification.reader_id != user.reader.id):
        return jsonify({"error": "Forbidden"}), 403
    
    notification.mark_read()
    db.session.commit()
    
    return jsonify({"status": "success", "is_read": True})

