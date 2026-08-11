from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="player")  # 'admin' or 'player'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    games = db.relationship("Game", backref="user", lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def games_started_today(self):
        today = date.today()
        return Game.query.filter(
            Game.user_id == self.id,
            db.func.date(Game.started_at) == today,
        ).count()

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5), unique=True, nullable=False)

    def __repr__(self):
        return f"<Word {self.text}>"


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False)
    status = db.Column(db.String(15), nullable=False, default="in_progress")
    # 'in_progress', 'won', 'lost'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    word = db.relationship("Word")
    guesses = db.relationship(
        "Guess", backref="game", lazy=True, order_by="Guess.guess_number"
    )

    def __repr__(self):
        return f"<Game {self.id} user={self.user_id} status={self.status}>"


class Guess(db.Model):
    __tablename__ = "guesses"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    guess_number = db.Column(db.Integer, nullable=False)  # 1..MAX_GUESSES
    guess_text = db.Column(db.String(5), nullable=False)
    result = db.Column(db.String(30), nullable=False)  # comma separated: green,orange,grey,...
    guessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Guess {self.guess_text} game={self.game_id}>"
