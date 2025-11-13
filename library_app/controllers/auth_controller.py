from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for

from library_app.services.auth_service import (
    AuthResult,
    authenticate,
    is_authenticated,
    login_user,
    logout_user,
    register_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _safe_next(target: str | None) -> str | None:
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.netloc:
        return None
    return target


@auth_bp.before_app_request
def load_logged_user() -> None:
    from library_app.services.auth_service import load_logged_in_user

    load_logged_in_user()


@auth_bp.get("/login")
def login_form():
    if is_authenticated():
        flash("Ви вже авторизовані.", "info")
        return redirect(url_for("store.catalog"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_submit():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    result: AuthResult = authenticate(email, password)
    if not result.success or result.user is None:
        flash(result.message, "danger")
        return redirect(url_for("auth.login_form"))

    login_user(result.user)
    flash("Вітаємо, вхід успішний ✅", "success")
    next_url = _safe_next(request.form.get("next") or request.args.get("next"))
    return redirect(next_url or url_for("store.catalog"))


@auth_bp.get("/signup")
def signup_form():
    if is_authenticated():
        flash("Ви вже авторизовані.", "info")
        return redirect(url_for("store.catalog"))
    return render_template("auth/signup.html")


@auth_bp.post("/signup")
def signup_submit():
    data = {
        "full_name": request.form.get("full_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "password": request.form.get("password", ""),
        "address": request.form.get("address", "").strip(),
        "phone": request.form.get("phone", "").strip(),
    }
    if not all(data.values()):
        flash("Будь ласка, заповніть усі поля.", "danger")
        return redirect(url_for("auth.signup_form"))

    result = register_user(**data)
    if not result.success or result.user is None:
        flash(result.message, "danger")
        return redirect(url_for("auth.signup_form"))

    login_user(result.user)
    role_msg = (
        "Створено адміністратора. Ви маєте повний доступ."
        if result.user.is_admin()
        else "Акаунт створено. Доступ як читач."
    )
    flash(f"{result.message} {role_msg}", "success")
    return redirect(url_for("store.catalog"))


@auth_bp.post("/logout")
def logout():
    if is_authenticated():
        logout_user()
        flash("Вихід виконано.", "info")
    return redirect(url_for("auth.login_form"))

