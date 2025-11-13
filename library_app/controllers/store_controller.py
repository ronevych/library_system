from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from library_app.services import book_repository, rental_repository
from library_app.services.auth_service import current_user, login_required
from library_app.services.rental_service import RentalError, rental_service

store_bp = Blueprint("store", __name__, url_prefix="/store")


@store_bp.get("/")
def catalog():
    query = request.args.get("q", "").strip()
    if query:
        books = book_repository.search_available(query)
    else:
        books = book_repository.find_available()
    return render_template("store/catalog.html", books=books, query=query)


@store_bp.post("/rent")
@login_required
def rent_book():
    user = current_user()
    if user is None or user.reader is None:
        if request.is_json:
            return jsonify({"error": "reader_profile_missing"}), 400
        flash("Не вдалося визначити профіль читача.", "danger")
        return redirect(url_for("store.catalog"))

    payload = request.get_json(silent=True)
    if payload:
        book_id = payload.get("book_id")
        days = payload.get("days", 14)
    else:
        book_id = request.form.get("book_id")
        days = request.form.get("days", "14")

    if not book_id:
        if payload:
            return jsonify({"error": "book_id_required"}), 400
        flash("Будь ласка, оберіть книгу.", "warning")
        return redirect(url_for("store.catalog"))

    try:
        rental = rental_service.rent_book(
            book_id=int(book_id),
            reader_id=user.reader.id,
            days=int(days),
        )
    except RentalError as exc:
        if payload:
            return jsonify({"error": str(exc)}), 400
        flash(str(exc), "danger")
        return redirect(url_for("store.catalog"))

    if payload:
        return (
            jsonify(
                {
                    "rental_id": rental.id,
                    "book_id": rental.book_id,
                    "reader_id": rental.reader_id,
                    "due_date": rental.due_date.isoformat(),
                }
            ),
            201,
        )

    flash("Замовлення оформлено ✅. Очікуйте підтвердження бібліотекаря.", "success")
    return redirect(url_for("store.catalog"))


@store_bp.get("/my-rentals")
@login_required
def my_rentals():
    user = current_user()
    if user is None or user.reader is None:
        if request.accept_mimetypes.accept_json:
            return jsonify({"error": "reader_profile_missing"}), 400
        flash("Не вдалося визначити профіль читача.", "danger")
        return redirect(url_for("store.catalog"))

    rentals = rental_repository.for_reader(user.reader.id)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(
            [
                {
                    "id": rental.id,
                    "book": rental.book.title,
                    "rent_date": rental.rent_date.isoformat(),
                    "due_date": rental.due_date.isoformat(),
                    "return_date": rental.return_date.isoformat()
                    if rental.return_date
                    else None,
                    "fine_amount": rental.fine_amount,
                }
                for rental in rentals
            ]
        )

    return render_template("store/my_rentals.html", rentals=rentals)

