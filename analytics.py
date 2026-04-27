from db import cur, conn

def log_watch(user, movie):
    cur.execute("INSERT INTO history VALUES (?, ?)", (user, movie))
    conn.commit()

def get_history(user):
    cur.execute("SELECT movie FROM history WHERE user=?", (user,))
    return [r[0] for r in cur.fetchall()]