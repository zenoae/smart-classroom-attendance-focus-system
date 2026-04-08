from flask import Flask

from app.extensions import db, migrate
from app.views.main import main_bp
from app.views.attendance import attendance_bp
from app.views.focus import focus_bp
from app.views.stats import stats_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smart_classroom.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(focus_bp, url_prefix="/focus")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    return app

