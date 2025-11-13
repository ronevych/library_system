from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from library_app.models import db
from library_app.models.book import Book
from library_app.services import book_repository
from library_app.services.auth_service import admin_required

books_bp = Blueprint("books", __name__)


@books_bp.before_request
@admin_required
def ensure_admin():
    return None


@books_bp.get("/")
def list_books():
    books = book_repository.all()
    return render_template("books.html", books=books)


@books_bp.post("/")
def create_book():
    payload = request.get_json(silent=True)
    if payload:
        book = Book(
            title=payload["title"],
            author=payload["author"],
            genre=payload["genre"],
            collateral_value=float(payload["collateral_value"]),
            daily_rent_price=float(payload["daily_rent_price"]),
            available_copies=int(payload.get("available_copies", 1)),
        )
        book_repository.add(book)
        return jsonify({"id": book.id}), 201

    form = request.form
    book = Book(
        title=form["title"],
        author=form["author"],
        genre=form["genre"],
        collateral_value=float(form["collateral_value"]),
        daily_rent_price=float(form["daily_rent_price"]),
        available_copies=int(form.get("available_copies", 1)),
    )
    book_repository.add(book)
    flash("Книгу успішно додано ✅", "success")
    return redirect(url_for("books.list_books"))


@books_bp.get("/<int:book_id>")
def get_book(book_id: int):
    book = book_repository.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "collateral_value": book.collateral_value,
            "daily_rent_price": book.daily_rent_price,
            "available_copies": book.available_copies,
        }
    )


@books_bp.put("/<int:book_id>")
@books_bp.patch("/<int:book_id>")
def update_book(book_id: int):
    book = book_repository.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True) or {}
    for field in ["title", "author", "genre"]:
        if field in data:
            setattr(book, field, data[field])
    for numeric in ["collateral_value", "daily_rent_price", "available_copies"]:
        if numeric in data:
            setattr(book, numeric, float(data[numeric]))

    db.session.commit()
    return jsonify({"status": "updated"})


@books_bp.delete("/<int:book_id>")
def delete_book(book_id: int):
    book = book_repository.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    book_repository.delete(book)
    return jsonify({"status": "deleted"})

