import hashlib
from db import cur, conn

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def create_user(u, p):
    try:
        cur.execute("INSERT INTO users VALUES (?, ?)", (u, hash_password(p)))
        conn.commit()
        return True
    except:
        return False

def login_user(u, p):
    cur.execute("SELECT password FROM users WHERE username=?", (u,))
    row = cur.fetchone()
    return row and row[0] == hash_password(p)