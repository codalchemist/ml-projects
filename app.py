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
def get_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    c_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"

    try:
        r = requests.get(url, timeout=8)
        c = requests.get(c_url, timeout=8)

        if r.status_code != 200:
            return None

        movie_data = r.json()
        credits_data = c.json() if c.status_code == 200 else {}

        title = movie_data.get("title", "Unknown")
        rating = movie_data.get("vote_average", 0)
        overview = movie_data.get("overview", "No description available")

        genres = ", ".join(
            g["name"] for g in movie_data.get("genres", [])
        ) or "N/A"

        actors = ", ".join(
            a["name"] for a in credits_data.get("cast", [])[:5]
        ) or "N/A"

        age = "18+" if movie_data.get("adult") else "All / 13+ Safe"

        link = f"https://www.themoviedb.org/movie/{movie_id}"

        poster_path = movie_data.get("poster_path")
        poster = (
            "https://image.tmdb.org/t/p/w500" + poster_path
            if poster_path else PLACEHOLDER
        )

        return title, rating, overview, genres, actors, age, link, poster

    except requests.exceptions.RequestException:
        return None

def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]
    return scores


if "user" not in st.session_state:
    st.session_state.user = None


st.title("🎬 WatchNext")
genre_list = ["All", "Action", "Romance", "Comedy", "Drama", "Horror", "Sci-Fi", "Thriller"]

selected_genre = st.selectbox("🎭 Choose Mood / Genre", genre_list)


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

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    tab1, tab2, tab3 = st.tabs(["🎬 For You", "🔥 Trending", "📜 History"])

    with tab1:

        if selected_genre == "All":
            filtered_movies = movies
        else:
            filtered_movies = movies[
                movies["tags"].str.contains(selected_genre.lower(), na=False)
            ]

        movie = st.selectbox("🎬 Pick a movie", filtered_movies["title"].values)

        if st.button("Recommend"):

            recs = recommend(movie)

            valid_movies = []

            for idx, _ in recs:
                movie_id = movies.iloc[idx]["id"]
                data = get_details(movie_id)

                if data:
                    valid_movies.append(data)

                if len(valid_movies) == 5:
                    break

            cols = st.columns(5)

            for i, data in enumerate(valid_movies):
                title, rating, overview, genres, actors, age, link, poster = data

                with cols[i]:
                    st.image(poster, use_container_width=True)
                    st.markdown(f"### {title}")
                    st.write(f"⭐ Rating: {rating}")
                    st.write(f"🎭 {genres}")
                    st.write(f"👥 {actors}")
                    st.write(f"🔞 {age}")
                    st.write(overview[:150] + "...")
                    st.markdown(f"[🎬 Watch]({link})")

            log_history(st.session_state.user, movie)

    with tab2:

        st.subheader("🔥 Trending Now")

        trending = movies.sample(5)

        cols = st.columns(5)

        for i in range(5):

            movie_id = trending.iloc[i]["id"]
            data = get_details(movie_id)

            if data:
                title, rating, overview, genres, actors, age, link, poster = data

                with cols[i]:
                    st.image(poster, use_container_width=True)
                    st.caption(title)

    with tab3:

        st.subheader("📜 Your Watch History")

        history = get_history(st.session_state.user)

        if not history:
            st.write("No watch history yet")
        else:
            for h in reversed(history):
                st.write("•", h)

st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #0e1117;
    color: white;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    z-index: 999;
    border-top: 1px solid #333;
}
</style>

<div class="footer">
⭐💛 Designed and Developed by CHIRAG NAGPAL © 2026 — All rights reserved
</div>
""", unsafe_allow_html=True)