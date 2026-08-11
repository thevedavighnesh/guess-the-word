from datetime import datetime, date
from functools import wraps

from flask import render_template, request, abort
from flask_login import login_required, current_user

from extensions import db
from models import User, Game
from . import admin_bp


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    users = User.query.filter_by(role="player").order_by(User.username).all()
    return render_template("admin_dashboard.html", users=users)


@admin_bp.route("/daily")
@login_required
@admin_required
def daily_report():
    date_str = request.args.get("date", "")
    try:
        report_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        report_date = date.today()

    games_that_day = Game.query.filter(db.func.date(Game.started_at) == report_date).all()

    distinct_users = {g.user_id for g in games_that_day}
    correct_guesses = sum(1 for g in games_that_day if g.status == "won")

    return render_template(
        "admin_daily.html",
        report_date=report_date,
        num_users=len(distinct_users),
        num_correct=correct_guesses,
        num_games=len(games_that_day),
    )


@admin_bp.route("/user")
@login_required
@admin_required
def user_report():
    username = request.args.get("username", "")
    rows = []
    selected_user = None

    if username:
        selected_user = User.query.filter_by(username=username).first()
        if selected_user:
            games = Game.query.filter_by(user_id=selected_user.id).order_by(Game.started_at).all()
            by_date = {}
            for g in games:
                d = g.started_at.date()
                bucket = by_date.setdefault(d, {"tried": 0, "correct": 0})
                bucket["tried"] += 1
                if g.status == "won":
                    bucket["correct"] += 1
            rows = [
                {"date": d, "tried": v["tried"], "correct": v["correct"]}
                for d, v in sorted(by_date.items())
            ]

    users = User.query.filter_by(role="player").order_by(User.username).all()
    return render_template(
        "admin_user.html",
        users=users,
        selected_username=username,
        selected_user=selected_user,
        rows=rows,
    )
