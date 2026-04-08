from datetime import datetime

import cv2
import numpy as np
from flask import Blueprint, render_template, request

from app.extensions import db
from app.models import ClassSession, FocusRecord, Student


focus_bp = Blueprint("focus", __name__, template_folder="../../templates")


def _estimate_focus_from_frame(frame: np.ndarray) -> float:
    """
    基于人脸位置的一个简单“专注度”估计：
    - 检测到人脸且位于画面中央、占比适中 → 分数高
    - 未检测到人脸 / 人脸偏离画面中心很多 → 分数低
    """
    if frame is None or frame.size == 0:
        return 0.0

    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return 0.0

    # 简化：只取第一张人脸
    x, y, fw, fh = faces[0]
    face_cx = x + fw / 2.0
    face_cy = y + fh / 2.0

    center_x, center_y = w / 2.0, h / 2.0
    dx_norm = abs(face_cx - center_x) / center_x
    dy_norm = abs(face_cy - center_y) / center_y

    # 人脸越接近画面中心，分数越高
    position_score = max(0.0, 1.0 - (dx_norm + dy_norm) / 2.0 * 1.5)

    # 人脸在画面中占比：太小可能是离得很远或不专心
    face_area = fw * fh
    frame_area = w * h
    area_ratio = face_area / frame_area if frame_area > 0 else 0.0
    size_score = max(0.0, min(1.0, (area_ratio - 0.02) / 0.08))  # 大约 2%~10% 区间映射到 0~1

    score = 0.7 * position_score + 0.3 * size_score
    return float(max(0.0, min(1.0, score)))


@focus_bp.route("/analyze", methods=["GET", "POST"])
def analyze_focus():
    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()

    if request.method == "POST":
        session_id = int(request.form.get("session_id"))
        file = request.files.get("image") or request.files.get("video")
        if not file:
            return render_template("focus_analyze.html", sessions=sessions, error="请上传课堂图片")

        temp_data = file.read()
        nparr = np.frombuffer(temp_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return render_template("focus_analyze.html", sessions=sessions, error="图片解析失败")

        session = ClassSession.query.get_or_404(session_id)
        student = Student.query.first()
        if student is None:
            return render_template("focus_analyze.html", sessions=sessions, error="系统中没有学生信息")

        score = _estimate_focus_from_frame(frame)
        level = "high"
        if score < 0.4:
            level = "low"
        elif score < 0.7:
            level = "medium"

        record = FocusRecord(
            session_id=session.id,
            student_id=student.id,
            timestamp=datetime.utcnow(),
            score=score,
            level=level,
        )
        db.session.add(record)
        db.session.commit()

        return render_template(
            "focus_analyze.html",
            sessions=sessions,
            success=True,
            score=round(score, 2),
            level=level,
        )

    return render_template("focus_analyze.html", sessions=sessions)

