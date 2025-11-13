from __future__ import annotations
from datetime import datetime
from flask import Flask, redirect, url_for

from library_app.config import init_extensions
from library_app.controllers.auth_controller import auth_bp
from library_app.controllers.books_controller import books_bp
from library_app.controllers.notifications_controller import notifications_bp
from library_app.controllers.readers_controller import readers_bp
from library_app.controllers.rentals_controller import rentals_bp
from library_app.controllers.reports_controller import reports_bp
from library_app.controllers.store_controller import store_bp
from library_app.services.notification_service import NotificationService
from library_app.services.auth_service import current_user, is_authenticated, is_admin


def create_app(config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if config:
        app.config.update(config)
    init_extensions(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(readers_bp, url_prefix="/readers")
    app.register_blueprint(rentals_bp, url_prefix="/rentals")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")

    # Template helpers
    @app.context_processor
    def inject_now() -> dict[str, callable]:
        return {
            "now": datetime.utcnow,
            "current_user": current_user,
            "is_authenticated": is_authenticated,
            "is_admin": is_admin,
        }

    @app.route("/")
    def index():
        return redirect(url_for("store.catalog"))

    # Attach notification service (Observer pattern) to app context
    NotificationService.bootstrap()

    return app
