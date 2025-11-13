from __future__ import annotations

from dataclasses import dataclass
from functools import wraps

from flask import flash, g, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from library_app.models.reader import Reader, ReaderCategory
from library_app.models.user import User, UserRole
from library_app.services import reader_repository, user_repository


@dataclass
class AuthResult:
    success: bool
    message: str
    user: User | None = None


SESSION_USER_KEY = "user_id"


def register_user(
    full_name: str,
    email: str,
    password: str,
    address: str,
    phone: str,
) -> AuthResult:
    email_normalized = email.strip().lower()
    existing = user_repository.find_by_email(email_normalized)
    if existing:
        return AuthResult(False, "Користувач із такою електронною поштою вже існує.")

    role = UserRole.USER
    if not user_repository.has_admin():
        role = UserRole.ADMIN

    reader = Reader(
        full_name=full_name,
        address=address,
        phone=phone,
        category=ReaderCategory.REGULAR,
    )
    reader_repository.add(reader)

    user = User(
        email=email_normalized,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        role=role,
        reader_id=reader.id,
    )
    user_repository.add(user)
    return AuthResult(True, "Реєстрацію успішно завершено.", user)


def authenticate(email: str, password: str) -> AuthResult:
    email_normalized = email.strip().lower()
    user = user_repository.find_by_email(email_normalized)
    if user is None or not check_password_hash(user.password_hash, password):
        return AuthResult(False, "Невірна пара email/пароль.")
    return AuthResult(True, "Вхід виконано.", user)


def login_user(user: User) -> None:
    session[SESSION_USER_KEY] = user.id


def logout_user() -> None:
    session.pop(SESSION_USER_KEY, None)


def load_logged_in_user() -> None:
    user_id = session.get(SESSION_USER_KEY)
    if user_id is None:
        g.current_user = None
    else:
        g.current_user = user_repository.get(user_id)


def current_user() -> User | None:
    return getattr(g, "current_user", None)


def is_authenticated() -> bool:
    return current_user() is not None


def is_admin() -> bool:
    user = current_user()
    return bool(user and user.is_admin())


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not is_authenticated():
            if request.is_json or request.accept_mimetypes.accept_json:
                return jsonify({"error": "authentication_required"}), 401
            flash("Потрібно увійти до системи.", "warning")
            next_target = request.url if request.method == "GET" else url_for("store.catalog")
            return redirect(url_for("auth.login_form", next=next_target))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not is_authenticated():
            if request.is_json or request.accept_mimetypes.accept_json:
                return jsonify({"error": "authentication_required"}), 401
            flash("Потрібно увійти до системи.", "warning")
            next_target = request.url if request.method == "GET" else url_for("store.catalog")
            return redirect(url_for("auth.login_form", next=next_target))
        if not is_admin():
            if request.is_json or request.accept_mimetypes.accept_json:
                return jsonify({"error": "forbidden"}), 403
            flash("Недостатньо прав для доступу.", "danger")
            return redirect(url_for("store.catalog"))
        return view(*args, **kwargs)

    return wrapped_view


__all__ = [
    "register_user",
    "authenticate",
    "login_user",
    "logout_user",
    "load_logged_in_user",
    "current_user",
    "is_authenticated",
    "is_admin",
    "login_required",
    "admin_required",
    "AuthResult",
]

