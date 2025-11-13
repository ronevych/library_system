from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, render_template, request

from library_app.services.report_service import report_service
from library_app.services.auth_service import admin_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.before_request
@admin_required
def ensure_admin():
    return None


@reports_bp.get("/")
def overview():
    inventory = report_service.book_inventory_report()
    overdue = report_service.overdue_report()
    return render_template(
        "reports.html",
        inventory=inventory,
        overdue=overdue,
    )


@reports_bp.get("/financial")
def financial_report():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "start and end dates required"}), 400
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    summary = report_service.financial_report(start_date, end_date)
    return jsonify(
        {
            "total_income": summary.total_income,
            "payments_count": summary.payments_count,
        }
    )

