from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from library_app.models import db
from library_app.models.reader import ReaderCategory
from library_app.services import reader_repository
from library_app.services.reader_factory import get_reader_creator
from library_app.services.auth_service import admin_required

readers_bp = Blueprint("readers", __name__)


@readers_bp.before_request
@admin_required
def ensure_admin():
    return None


@readers_bp.get("/")
def list_readers():
    readers = reader_repository.all()
    return render_template("readers.html", readers=readers, categories=list(ReaderCategory))


@readers_bp.post("/")
def create_reader():
    payload = request.get_json(silent=True)
    if payload:
        category = ReaderCategory(payload.get("category", ReaderCategory.REGULAR))
        creator = get_reader_creator(category)
        reader = creator.create_reader(
            full_name=payload["full_name"],
            address=payload["address"],
            phone=payload["phone"],
        )
        reader_repository.add(reader)
        return jsonify({"id": reader.id}), 201

    form = request.form
    category = ReaderCategory(form.get("category", ReaderCategory.REGULAR))
    creator = get_reader_creator(category)
    reader = creator.create_reader(
        full_name=form["full_name"],
        address=form["address"],
        phone=form["phone"],
    )
    reader_repository.add(reader)
    flash("Читача успішно створено ✅", "success")
    return redirect(url_for("readers.list_readers"))


@readers_bp.get("/<int:reader_id>")
def get_reader(reader_id: int):
    reader = reader_repository.get(reader_id)
    if reader is None:
        return jsonify({"error": "Reader not found"}), 404
    return jsonify(
        {
            "id": reader.id,
            "full_name": reader.full_name,
            "address": reader.address,
            "phone": reader.phone,
            "category": reader.category.value,
        }
    )


@readers_bp.put("/<int:reader_id>")
@readers_bp.patch("/<int:reader_id>")
def update_reader(reader_id: int):
    reader = reader_repository.get(reader_id)
    if reader is None:
        return jsonify({"error": "Reader not found"}), 404

    data = request.get_json(silent=True) or {}
    for field in ["full_name", "address", "phone"]:
        if field in data:
            setattr(reader, field, data[field])
    if "category" in data:
        reader.category = ReaderCategory(data["category"])
    db.session.commit()
    return jsonify({"status": "updated"})


@readers_bp.delete("/<int:reader_id>")
def delete_reader(reader_id: int):
    reader = reader_repository.get(reader_id)
    if reader is None:
        return jsonify({"error": "Reader not found"}), 404
    reader_repository.delete(reader)
    return jsonify({"status": "deleted"})

