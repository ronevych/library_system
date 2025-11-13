from __future__ import annotations

from library_app.config import Database

db = Database.instance()

# Import models to ensure metadata is registered for create_all
from library_app.models import book, reader, rental, payment, notification, user  # noqa: E402,F401

__all__ = ["db", "book", "reader", "rental", "payment", "notification", "user"]

