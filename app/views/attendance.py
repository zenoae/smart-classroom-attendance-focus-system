from datetime import datetime

import cv2
import numpy as np
from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import AttendanceRecord, ClassSession, Course, Student
from app.services.face_recognition_service import enroll_student_face, recognize_student


attendance_bp = Blueprint("attendance", __name__, template_folder="../../templates")


@attendance_bp.route("/courses", methods=["GET", "POST"])
def manage_courses():
    courses = Course.query.order_by(Course.id.desc()).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        teacher = request.form.get("teacher", "").strip()
        if not name:
            flash("课程名称不能为空", "danger")
        else:
            course = Course(name=name, teacher=teacher)
            db.session.add(course)
            db.session.commit()
            flash("课程已创建", "success")
            return redirect(url_for("attendance.manage_courses"))
    return render_template("courses.html", courses=courses)


@attendance_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
def delete_course(course_id: int):
    course = Course.query.get_or_404(course_id)
    if course.sessions:
        flash("该课程已经有关联的课堂记录，无法删除", "warning")
    else:
        db.session.delete(course)
        db.session.commit()
        flash("课程已删除", "success")
    return redirect(url_for("attendance.manage_courses"))


@attendance_bp.route("/students")
def list_students():
    students = Student.query.all()
    return render_template("students.html", students=students)


@attendance_bp.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_no = request.form.get("student_no", "").strip()
        name = request.form.get("name", "").strip()
        clazz = request.form.get("clazz", "").strip()
        if not student_no or not name:
            flash("学号和姓名不能为空", "danger")
        else:
            student = Student(student_no=student_no, name=name, clazz=clazz)
            db.session.add(student)
            db.session.commit()
            flash("学生信息已保存，请录入人脸", "success")
            return redirect(url_for("attendance.capture_face", student_id=student.id))
    return render_template("add_student.html")


@attendance_bp.route("/students/<int:student_id>/capture", methods=["GET"])
def capture_face(student_id: int):
    student = Student.query.get_or_404(student_id)
    return render_template("capture_face.html", student=student)


@attendance_bp.route("/students/<int:student_id>/capture_frame", methods=["POST"])
def capture_face_frame(student_id: int):
    student = Student.query.get_or_404(student_id)
    file = request.files.get("frame")
    if not file:
        return {"success": False, "message": "未接收到图像"}, 400
    file_bytes = file.read()
    nparr = np.frombuffer(file_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    enroll_student_face(student, frame)
    return {"success": True}


@attendance_bp.route("/sessions")
def list_sessions():
    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()
    return render_template("sessions.html", sessions=sessions)


@attendance_bp.route("/sessions/start", methods=["GET", "POST"])
def start_session():
    courses = Course.query.all()
    if request.method == "POST":
        course_id = request.form.get("course_id")
        classroom = request.form.get("classroom", "").strip()
        if not course_id:
            flash("必须选择课程", "danger")
        else:
            session = ClassSession(course_id=int(course_id), classroom=classroom, start_time=datetime.utcnow())
            db.session.add(session)
            db.session.commit()
            return redirect(url_for("attendance.run_session", session_id=session.id))
    return render_template("start_session.html", courses=courses)


@attendance_bp.route("/sessions/<int:session_id>/run")
def run_session(session_id: int):
    session = ClassSession.query.get_or_404(session_id)
    return render_template("run_session.html", session=session)


@attendance_bp.route("/sessions/<int:session_id>/capture_frame", methods=["POST"])
def capture_attendance_frame(session_id: int):
    session = ClassSession.query.get_or_404(session_id)
    file = request.files.get("frame")
    if not file:
        return {"success": False, "message": "未接收到图像"}, 400
    file_bytes = file.read()
    nparr = np.frombuffer(file_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    student = recognize_student(frame)
    if not student:
        return {"success": False, "message": "未识别到已注册学生"}, 200
    record = AttendanceRecord(session_id=session.id, student_id=student.id, status="present")
    db.session.add(record)
    db.session.commit()
    return {"success": True, "student_name": student.name}

