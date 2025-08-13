
# Make register_user and login_user importable
__all__ = ["register_user", "login_user"]
import os
import json
import re
from .utils import hash_password, verify_password
from .constants import ALLOWED_CATEGORIES, USERNAME_PATTERN, PASSWORD_MIN_LEN

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def get_user_file(username: str) -> str:
    return os.path.join(DATA_DIR, f"{username}.json")

def user_exists(username: str) -> bool:
    return os.path.exists(get_user_file(username))

def register_user(username: str, password: str) -> bool:
    # Enforce username pattern
    if not re.match(USERNAME_PATTERN, username):
        print("Error: Username must contain only letters, numbers, or underscore.")
        return False
    if user_exists(username):
        print("Error: Username already exists.")
        return False
    if len(password) < PASSWORD_MIN_LEN:
        print(f"Error: Password must be at least {PASSWORD_MIN_LEN} characters.")
        return False
    ph, salt, iters = hash_password(password)
    user_data = {
        "auth": {
            "username": username,
            "password_hash": ph,
            "salt": salt,
            "iterations": iters
        },
        "transactions": [],
        "budgets": {cat: 0 for cat in ALLOWED_CATEGORIES}
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_user_file(username), 'w') as f:
        json.dump(user_data, f, indent=4)
    print(f"User '{username}' registered successfully.")
    return True

def login_user(username: str, password: str) -> dict:
    if not user_exists(username):
        print("Error: Username does not exist.")
        return None
    with open(get_user_file(username), 'r') as f:
        user_data = json.load(f)
    auth = user_data.get("auth", {})
    if not verify_password(password, auth.get("salt", ""), auth.get("password_hash", ""), auth.get("iterations", 100_000)):
        print("Error: Incorrect password.")
        return None
    print(f"Welcome, {username}!")
    return user_data

