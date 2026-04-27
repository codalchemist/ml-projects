import sqlite3

conn = sqlite3.connect("analytics.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS history (
    user TEXT,
    movie TEXT
)
""")

def log_watch(user, movie):
    cur.execute("INSERT INTO history VALUES (?, ?)", (user, movie))
    conn.commit()

def get_history(user):
    cur.execute("SELECT movie FROM history WHERE user=?", (user,))
    return [row[0] for row in cur.fetchall()]