import sqlite3
import hashlib

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    if not username or not password:
        return False

    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cur.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )
    row = cur.fetchone()

    if row and row[0] == hash_password(password):
        return True

    return False