import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "guess_the_word.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Game rules
    WORD_LENGTH = 5
    MAX_GUESSES = 5
    MAX_GAMES_PER_DAY = 3
