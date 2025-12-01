from __future__ import annotations

from datetime import date

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from library_app.models import db
from library_app.services import book_repository, reader_repository, rental_repository
from library_app.services.auth_service import admin_required
from library_app.services.rental_service import RentalError, rental_service

rentals_bp = Blueprint("rentals", __name__)


@rentals_bp.before_request
@admin_required
def ensure_admin():
    return None


@rentals_bp.get("/")
def list_rentals():
    rentals = rental_repository.all()
    books = book_repository.find_available()
    readers = reader_repository.all()
    return render_template(
        "rentals.html",
        rentals=rentals,
        books=books,
        readers=readers,
        view="all",
    )


@rentals_bp.post("/")
def create_rental():
    payload = request.get_json(silent=True)
    try:
        if payload:
            rental = rental_service.rent_book(
                book_id=int(payload["book_id"]),
                reader_id=int(payload["reader_id"]),
                days=int(payload.get("days", 14)),
            )
        else:
            rental = rental_service.rent_book(
                book_id=int(request.form["book_id"]),
                reader_id=int(request.form["reader_id"]),
                days=int(request.form.get("days", 14)),
            )
    except RentalError as exc:
        db.session.rollback()
        if payload:
            return jsonify({"error": str(exc)}), 400
        flash(str(exc), "danger")
        return redirect(url_for("rentals.list_rentals"))

    if payload:
        return jsonify({"id": rental.id}), 201

    flash("Оформлено ✅", "success")
    return redirect(url_for("rentals.list_rentals"))


@rentals_bp.post("/<int:rental_id>/return")
def return_rental(rental_id: int):
    data = request.get_json(silent=True) or {}
    
    # Parse return date
    if "return_date" in data:
        return_date = date.fromisoformat(data["return_date"])
    elif request.form.get("return_date"):
        return_date = date.fromisoformat(request.form["return_date"])
    else:
        return_date = None
    
    # Parse damage information
    damage_amount = 0.0
    damage_comment = None
    
    if data:
        # JSON request
        if data.get("is_damaged") == "yes":
            damage_amount = float(data.get("damage_amount", 0) or 0)
            damage_comment = data.get("damage_comment") or None
    else:
        # Form request
        if request.form.get("is_damaged") == "yes":
            damage_amount = float(request.form.get("damage_amount", 0) or 0)
            damage_comment = request.form.get("damage_comment") or None
    
    try:
        summary = rental_service.return_book(
            rental_id,
            return_date=return_date,
            damage_amount=damage_amount,
            damage_comment=damage_comment,
        )
    except RentalError as exc:
        db.session.rollback()
        if request.is_json:
            return jsonify({"error": str(exc)}), 400
        flash(str(exc), "danger")
        return redirect(url_for("rentals.list_rentals"))

    if request.is_json:
        return jsonify(
            {
                "amount_due": summary.amount_due,
                "discount_applied": summary.discount_applied,
                "fine_amount": summary.fine_amount,
                "damage_amount": summary.damage_amount,
                "days_rented": summary.days_rented,
            }
        )

    rental = summary.rental
    message = (
        f"{rental.reader.full_name} повернув(-ла) «{rental.book.title}» ✅. "
        f"Книга була у користуванні {summary.days_rented} днів. "
        f"Отримано {summary.amount_due:.2f} грн."
    )
    if summary.damage_amount > 0:
        message += f" (штраф за пошкодження: {summary.damage_amount:.2f} грн)"
    flash(message, "success")
    return redirect(url_for("rentals.list_rentals"))


@rentals_bp.post("/check-overdue")
def trigger_overdue_check():
    rental_service.check_overdue_rentals()
    payload = request.get_json(silent=True)
    overdue = rental_repository.overdue_rentals()

    wants_json = payload is not None or (
        request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
    )
    if wants_json:
        return jsonify(
            {
                "status": "notifications dispatched",
                "overdue": [
                    {
                        "id": rental.id,
                        "book": rental.book.title,
                        "reader": rental.reader.full_name,
                        "due_date": rental.due_date.isoformat(),
                    }
                    for rental in overdue
                ],
            }
        )

    books = book_repository.find_available()
    readers = reader_repository.all()
    return render_template(
        "rentals.html",
        rentals=overdue,
        books=books,
        readers=readers,
        view="overdue",
    )

