from app import create_app
from extensions import db
from models import Word, User

WORDS = [
    "PLANT", "GRAPE", "HOUSE", "MOUSE", "STONE",
    "CRANE", "TRAIN", "FLAME", "BRAVE", "CHESS",
    "SPINE", "GLOBE", "QUILT", "VIVID", "WORLD",
    "LIGHT", "NIGHT", "SOUND", "RIVER", "OCEAN",
]

DEFAULT_ADMIN_USERNAME = "AdminUser"
DEFAULT_ADMIN_PASSWORD = "Admin1$pass"


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        added_words = 0
        for text in WORDS:
            if not Word.query.filter_by(text=text).first():
                db.session.add(Word(text=text))
                added_words += 1
        db.session.commit()
        print(f"Seeded {added_words} new word(s); {Word.query.count()} word(s) total.")

        if not User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first():
            admin = User(username=DEFAULT_ADMIN_USERNAME, role="admin")
            admin.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(
                f"Created default admin user -> username: {DEFAULT_ADMIN_USERNAME}, "
                f"password: {DEFAULT_ADMIN_PASSWORD}"
            )
        else:
            print("Default admin user already exists.")


if __name__ == "__main__":
    seed()
