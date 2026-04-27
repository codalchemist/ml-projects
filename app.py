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
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.hero-banner {
    position: relative;
    background-image:
        linear-gradient(
            90deg,
            rgba(11,15,25,0.95) 0%,
            rgba(11,15,25,0.75) 40%,
            rgba(11,15,25,0.35) 100%
        ),
        url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba');
    background-size: cover;
    background-position: center;
    border-radius: 24px;
    padding: 50px 40px;
    margin-bottom: 35px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    border: 1px solid rgba(255,255,255,0.05);
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 10px;
    color: white;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #d1d5db;
    max-width: 700px;
    line-height: 1.7;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 7rem;
    max-width: 1450px;
}

.stButton button {
    width: 100%;
    border-radius: 14px;
    height: 3.2rem;
    font-weight: 700;
    font-size: 1rem;
    background: linear-gradient(90deg, #e50914, #ff2d55);
    color: white;
    border: none;
    box-shadow: 0 8px 20px rgba(229,9,20,0.35);
    transition: all 0.25s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 28px rgba(229,9,20,0.45);
}

.movie-card {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    padding: 16px;
    border-radius: 16px;
    margin-top: 10px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 12px 28px rgba(0,0,0,0.30);
    transition: all 0.25s ease;
}

.movie-card h3 {
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.movie-card p {
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 8px;
}

.movie-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.45);
    border-color: rgba(229,9,20,0.35);
}
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}
label {
    font-weight: 600 !important;
    font-size: 1rem !important;
}

img {
    border-radius: 14px;
    transition: 0.25s ease;
}

img:hover {
    transform: scale(1.03);
}

div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    background: #1f2937 !important;
    border: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] {
    background: #111827;
}

.sidebar .sidebar-content {
    background: #0b0f19;
}
</style>
""", unsafe_allow_html=True)

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

    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )[1:10]

    return scores


if "user" not in st.session_state:
    st.session_state.user = None


st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎬 WatchNext</div>
    <div class="hero-subtitle">
        Discover your next obsession with AI-powered recommendations,
        trending picks, and personalized movie suggestions —
        all in one cinematic experience.
    </div>
</div>
""", unsafe_allow_html=True)
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

    st.sidebar.markdown("## 👤 Profile")
    st.sidebar.info(f"Logged in as **{st.session_state.user}**")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["🎬 For You", "🔥 Trending", "📜 History"])


    with tab1:

        st.markdown("## 🍿 Discover Your Next Watch")

        if selected_genre == "All":
            filtered_movies = movies
        else:
            filtered_movies = movies[
                movies["tags"].str.contains(selected_genre.lower(), na=False)
            ]

        movie = st.selectbox(
            "🎬 Pick a movie",
            filtered_movies["title"].values
        )

        if st.button("Recommend"):

            with st.spinner("Finding your next watch..."):

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

                    st.markdown(f"""
                    <div class="movie-card">
                        <h3>{title}</h3>
                        <p>⭐ <b>{rating:.1f} / 10</b></p>
                        <p><b>🎭 Genre:</b> {genres}</p>
                        <p><b>👥 Cast:</b> {actors}</p>
                        <p><b>🔞 Advisory:</b> {age}</p>
                        <p style='color:#9ca3af;'>{overview[:140]}...</p>
                        <a href="{link}" target="_blank" style="
                            color:#e50914;
                            font-weight:600;
                            text-decoration:none;
                        ">🎬 Watch on TMDB</a>
                    </div>
                    """, unsafe_allow_html=True)
            log_history(st.session_state.user, movie)


    with tab2:

        st.markdown("## 🔥 Trending This Week")
        st.caption("Popular picks across the platform")

        trending = movies.sample(5)
        cols = st.columns(5)

        for i in range(5):
            movie_id = trending.iloc[i]["id"]
            data = get_details(movie_id)

            if data:
                title, rating, overview, genres, actors, age, link, poster = data

                with cols[i]:
                    st.image(poster, use_container_width=True)

                    st.markdown(f"""
                    <div class="movie-card">
                        <h3>{title}</h3>
                        <p>⭐ <b>{rating:.1f} / 10</b></p>
                        <p style='color:#9ca3af;'>{genres}</p>
                    </div>
                    """, unsafe_allow_html=True)


    with tab3:

        st.markdown("## 📜 Your Watch History")

        history = get_history(st.session_state.user)

        if not history:
            st.info("No watch history yet")
        else:
            for i, h in enumerate(reversed(history), 1):
                st.markdown(f"**{i}.** {h}")
st.sidebar.caption("WatchNext v2.3")

st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background: #0b0f19;
    color: #9ca3af;
    text-align: center;
    padding: 12px;
    font-size: 14px;
    border-top: 1px solid #222;
    z-index: 999;
}
</style>

<div class="footer">
⭐💛 Designed and Developed by CHIRAG NAGPAL © 2026 — All rights reserved
</div>
""", unsafe_allow_html=True)