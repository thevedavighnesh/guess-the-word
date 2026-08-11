import re

# Username: at least 5 letters, and must contain both an uppercase and a
# lowercase letter somewhere in it.
USERNAME_MIN_LEN = 5

# Password: at least 5 characters, must contain at least one letter, one
# digit, and one of the special characters $ % * ! @
PASSWORD_MIN_LEN = 5
PASSWORD_SPECIAL_CHARS = "$%*!@"


def validate_username(username: str):
    """Returns (is_valid, error_message)."""
    if not username or len(username) < USERNAME_MIN_LEN:
        return False, f"Username must be at least {USERNAME_MIN_LEN} characters long."
    if not re.search(r"[a-z]", username):
        return False, "Username must contain at least one lowercase letter."
    if not re.search(r"[A-Z]", username):
        return False, "Username must contain at least one uppercase letter."
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""


def validate_password(password: str):
    """Returns (is_valid, error_message)."""
    if not password or len(password) < PASSWORD_MIN_LEN:
        return False, f"Password must be at least {PASSWORD_MIN_LEN} characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not any(ch in PASSWORD_SPECIAL_CHARS for ch in password):
        return False, f"Password must contain at least one special character ({PASSWORD_SPECIAL_CHARS})."
    return True, ""
