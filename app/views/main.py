from flask import Blueprint, render_template

from app.models import Course, Student

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    course_count = Course.query.count()
    student_count = Student.query.count()
    return render_template("index.html", course_count=course_count, student_count=student_count)

