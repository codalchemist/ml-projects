import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS history (
    user TEXT,
    movie TEXT
)
""")

conn.commit()

def log_watch(user, movie):
    cur.execute("INSERT INTO history (user, movie) VALUES (?, ?)", (user, movie))
    conn.commit()

def get_history(user):
    cur.execute("SELECT movie FROM history WHERE user=?", (user,))
    return [r[0] for r in cur.fetchall()]