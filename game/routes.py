import random
from datetime import datetime

from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models import Game, Guess, Word
from . import game_bp
from .logic import score_guess


def _active_game():
    return Game.query.filter_by(user_id=current_user.id, status="in_progress").first()


def _serialize_game(game):
    return {
        "game_id": game.id,
        "status": game.status,
        "max_guesses": current_app.config["MAX_GUESSES"],
        "word_length": current_app.config["WORD_LENGTH"],
        "guesses": [
            {
                "guess": g.guess_text,
                "result": g.result.split(","),
            }
            for g in game.guesses
        ],
        # Only reveal the answer once the game has ended.
        "answer": game.word.text if game.status != "in_progress" else None,
    }


@game_bp.route("/", methods=["GET"])
@login_required
def play():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    game = _active_game()
    games_today = current_user.games_started_today()
    max_per_day = current_app.config["MAX_GAMES_PER_DAY"]
    can_start_new = game is None and games_today < max_per_day

    return render_template(
        "game.html",
        game=_serialize_game(game) if game else None,
        games_today=games_today,
        max_per_day=max_per_day,
        can_start_new=can_start_new,
    )


@game_bp.route("/start", methods=["POST"])
@login_required
def start():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    if _active_game() is not None:
        flash("You already have a game in progress.", "error")
        return redirect(url_for("game.play"))

    games_today = current_user.games_started_today()
    max_per_day = current_app.config["MAX_GAMES_PER_DAY"]
    if games_today >= max_per_day:
        flash(f"You've reached the limit of {max_per_day} games today. Come back tomorrow!", "error")
        return redirect(url_for("game.play"))

    word = Word.query.order_by(db.func.random()).first()
    if word is None:
        flash("No words available. Please contact an admin.", "error")
        return redirect(url_for("game.play"))

    game = Game(user_id=current_user.id, word_id=word.id, status="in_progress")
    db.session.add(game)
    db.session.commit()

    return redirect(url_for("game.play"))


@game_bp.route("/guess", methods=["POST"])
@login_required
def guess():
    if current_user.is_admin:
        return jsonify({"error": "Admins cannot play."}), 403

    game = _active_game()
    if game is None:
        return jsonify({"error": "No game in progress. Start a new game first."}), 400

    word_length = current_app.config["WORD_LENGTH"]
    max_guesses = current_app.config["MAX_GUESSES"]

    data = request.get_json(silent=True) or request.form
    guess_text = (data.get("guess") or "").strip().upper()

    if len(guess_text) != word_length or not guess_text.isalpha():
        return jsonify({"error": f"Guess must be exactly {word_length} letters."}), 400

    guess_number = len(game.guesses) + 1
    if guess_number > max_guesses:
        return jsonify({"error": "No guesses remaining."}), 400

    answer = game.word.text
    result = score_guess(guess_text, answer)

    guess_row = Guess(
        game_id=game.id,
        guess_number=guess_number,
        guess_text=guess_text,
        result=",".join(result),
    )
    db.session.add(guess_row)

    won = guess_text == answer
    game_over = won or guess_number >= max_guesses

    if won:
        game.status = "won"
        game.ended_at = datetime.utcnow()
    elif guess_number >= max_guesses:
        game.status = "lost"
        game.ended_at = datetime.utcnow()

    db.session.commit()

    return jsonify(
        {
            "guess": guess_text,
            "result": result,
            "guess_number": guess_number,
            "won": won,
            "game_over": game_over,
            "status": game.status,
            "answer": answer if game_over else None,
        }
    )
