from __future__ import annotations

from library_app.models.user import UserRole
from library_app.services import user_repository


def signup_payload(email: str, full_name: str = "Тестовий Користувач"):
    return {
        "full_name": full_name,
        "email": email,
        "password": "secret123",
        "address": "м. Київ, вул. Тестова, 1",
        "phone": "+380971234567",
    }


def test_signup_creates_admin_then_user(app, client):
    response = client.post("/auth/signup", data=signup_payload("admin@example.com"), follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        admin_user = user_repository.find_by_email("admin@example.com")
        assert admin_user is not None
        assert admin_user.role == UserRole.ADMIN
        assert admin_user.reader is not None

    response = client.post(
        "/auth/signup",
        data=signup_payload("user@example.com", "Читач"),
        follow_redirects=False,
    )
    assert response.status_code == 302  # redirect to catalog

    with app.app_context():
        regular_user = user_repository.find_by_email("user@example.com")
        assert regular_user is not None
        assert regular_user.role == UserRole.USER
        assert regular_user.reader is not None


def test_login_stores_session(app, client):
    client.post("/auth/signup", data=signup_payload("login@example.com"), follow_redirects=True)
    client.post("/auth/logout")

    response = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with client.session_transaction() as sess:
        assert "user_id" in sess

