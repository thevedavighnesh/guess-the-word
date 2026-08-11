# Guess the Word

A 5-letter word guessing game (Wordle-style), built with Flask. Two roles:
**Player** (registers, plays the daily-limited guessing game) and **Admin**
(views daily and per-user reports).

## Setup

```bash
cd guess_the_word
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python seed_data.py              # creates DB, seeds 20 words + a default admin
python app.py                    # runs at http://localhost:5000
```

Default admin account created by `seed_data.py`:
- username: `AdminUser`
- password: `Admin1$pass`

(Change/remove this in `seed_data.py` before any real deployment.)

## How it maps to the requirements

- **Two user types** — `User.role` is `"admin"` or `"player"`. Registration
  (`/auth/register`) always creates a `player`; the admin account is seeded
  directly, since the spec doesn't call for self-service admin signup.
- **Registration validation**
  - Username: at least 5 characters, and must contain both an uppercase and
    a lowercase letter (letters/digits/underscore only).
  - Password: at least 5 characters, with at least one letter, one digit,
    and one of `$ % * !`. *(The spec's list of special characters was cut
    off after `$, %, *, and)` — I filled the fourth character in with `!`;
    this is easy to change in `auth/validators.py` if a different set was
    intended.)*
- **20 seed words** — `seed_data.py` loads 20 upper-case 5-letter English
  words into the `words` table.
- **Daily limit of 3 games** — enforced server-side in `game/routes.py`
  (`User.games_started_today()`), not just in the UI.
- **Gameplay**
  - Up to 5 guesses, 5-letter words, upper-case only, validated both
    client- and server-side.
  - Scoring (`game/logic.py`) marks each letter green (right letter, right
    spot), orange (right letter, wrong spot), or grey (not in the word),
    correctly handling repeated letters.
  - A win shows a "Congratulations!" modal; using all 5 guesses without a
    match shows "Better luck next time" — clicking OK in either case ends
    the game and returns to the play screen.
  - Earlier guesses stay visible in the grid, in the order they were
    guessed, while the game is in progress.
- **Persistence** — every game (`games` table) and every guess with its
  colour result (`guesses` table) is saved with a timestamp, so the full
  history of words given/guessed is recoverable per user and per day.
- **Admin reports** (`/admin`)
  - Daily report: pick a date, see number of distinct users who played and
    number of correct guesses (wins) that day.
  - User report: pick a player, see a per-date breakdown of words tried and
    correct guesses.

## Project structure

```
guess_the_word/
  app.py            # app factory, blueprint registration
  config.py          # settings (word length, guess/day limits, DB URL)
  extensions.py       # shared db / login_manager instances
  models.py           # User, Word, Game, Guess
  seed_data.py        # seeds 20 words + default admin
  auth/                # register / login / logout + validators
  game/                # play page, start game, submit guess, scoring logic
  admin/               # dashboard, daily report, user report
  templates/, static/  # UI
```

## Notes / assumptions

- Storage is SQLite by default (zero setup); set `DATABASE_URL` to point at
  Postgres/MySQL for production use — SQLAlchemy handles the rest.
- The "3 guesses [words] per day" limit is measured in the server's local
  calendar day.
- Admins are not able to play the game themselves (the spec describes them
  as configuring/running reports, not playing); this is easy to relax if
  that's not the intended read.
- This sandbox environment doesn't have outbound network/package-index
  access, so dependency installation and a live run couldn't be verified
  end-to-end here — `game/logic.py`'s scoring function was unit-tested
  standalone (including duplicate-letter cases) and every module was
  syntax-checked, but please run it locally before relying on it.

## Pushing to GitHub

```bash
cd guess_the_word
git init
git add .
git commit -m "Guess the Word: Flask implementation"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
