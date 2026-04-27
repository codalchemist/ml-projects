import streamlit as st
import pandas as pd
import requests
import sqlite3
import hashlib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

cv = CountVectorizer(max_features=5000, stop_words="english")
vector = cv.fit_transform(movies["tags"].fillna(""))
similarity = cosine_similarity(vector)

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS history (user TEXT, movie TEXT)")
conn.commit()


def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()


def signup(u, p):
    try:
        cur.execute("INSERT INTO users VALUES (?, ?)", (u, hash_pw(p)))
        conn.commit()
        return True
    except:
        return False


def login(u, p):
    cur.execute("SELECT password FROM users WHERE username=?", (u,))
    row = cur.fetchone()
    return row and row[0] == hash_pw(p)


def log_history(user, movie):
    cur.execute("INSERT INTO history VALUES (?, ?)", (user, movie))
    conn.commit()


def get_history(user):
    cur.execute("SELECT movie FROM history WHERE user=?", (user,))
    return [r[0] for r in cur.fetchall()]


def fetch(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return PLACEHOLDER
        data = r.json()
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else PLACEHOLDER
    except:
        return PLACEHOLDER


def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]
    return scores


if "user" not in st.session_state:
    st.session_state.user = None


st.title("🎬 WatchNext")


if not st.session_state.user:

    choice = st.sidebar.selectbox("Login / Signup", ["Login", "Signup"])
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if choice == "Signup":
        if st.sidebar.button("Create"):
            if signup(u, p):
                st.sidebar.success("Account created")
            else:
                st.sidebar.error("User exists")

    if choice == "Login":
        if st.sidebar.button("Login"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.sidebar.error("Invalid login")

else:

    st.sidebar.success(st.session_state.user)

    movie = st.selectbox("Pick a movie", movies["title"].values)

    if st.button("Recommend"):

        recs = recommend(movie)

        cols = st.columns(5)

        for i, (idx, _) in enumerate(recs):

            movie_id = movies.iloc[idx]["id"]

            with cols[i]:
                st.image(fetch(movie_id), use_container_width=True)
                st.caption(movies.iloc[idx]["title"])

        log_history(st.session_state.user, movie)

    st.subheader("History")
    for h in reversed(get_history(st.session_state.user)):
        st.write("•", h)


st.markdown("---")
st.markdown("⭐💛 Designed by CHIRAG NAGPAL © 2026 — All rights reserved")