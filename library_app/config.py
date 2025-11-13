from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Database:
    """Singleton wrapper around SQLAlchemy extension."""

    _instance: Optional[SQLAlchemy] = None

    @staticmethod
    def instance() -> SQLAlchemy:
        if Database._instance is None:
            Database._instance = SQLAlchemy()
        return Database._instance


def configure_app(app: Flask) -> None:
    """Apply default configuration to the Flask application."""
    base_dir = Path(app.root_path).parent
    db_path = base_dir / "library.db"

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path}")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    secret = os.getenv("FLASK_SECRET_KEY") or app.config.get("SECRET_KEY") or "dev-secret-key"
    app.config["SECRET_KEY"] = secret


def init_extensions(app: Flask) -> None:
    """Initialise Flask extensions with the configured app."""
    configure_app(app)
    db = Database.instance()
    db.init_app(app)


__all__ = ["Database", "configure_app", "init_extensions"]

