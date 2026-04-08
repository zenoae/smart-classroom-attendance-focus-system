from collections import defaultdict

from flask import Blueprint, render_template, request

from app.models import AttendanceRecord, ClassSession, FocusRecord


stats_bp = Blueprint("stats", __name__, template_folder="../../templates")


@stats_bp.route("/overview", methods=["GET"])
def overview():
    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()
    session_id = request.args.get("session_id", type=int)
    selected_session = None
    attendance_summary = {}
    focus_summary = {}

    if session_id:
        selected_session = ClassSession.query.get(session_id)
        if selected_session:
            records = AttendanceRecord.query.filter_by(session_id=session_id).all()
            status_count = defaultdict(int)
            for r in records:
                status_count[r.status] += 1
            attendance_summary = dict(status_count)

            focus_records = FocusRecord.query.filter_by(session_id=session_id).all()
            if focus_records:
                total = len(focus_records)
                level_count = defaultdict(int)
                for r in focus_records:
                    level_count[r.level] += 1
                focus_summary = {k: v / total for k, v in level_count.items()}

    return render_template(
        "stats_overview.html",
        sessions=sessions,
        selected_session=selected_session,
        attendance_summary=attendance_summary,
        focus_summary=focus_summary,
    )

