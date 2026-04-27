import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from auth import create_user, login_user
from analytics import log_watch, get_history
from recommender import hybrid_recommend, trending_movies

API_KEY = "3ee5dc2f1f74f34382d1b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

if "user" not in st.session_state:
    st.session_state.user = None

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return PLACEHOLDER
        data = r.json()
        path = data.get("poster_path")
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
        return PLACEHOLDER
    except:
        return PLACEHOLDER

def movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        c_url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}/credits?api_key={API_KEY}"

        r = requests.get(url, timeout=8).json()
        c = requests.get(c_url, timeout=8).json()

        title = r.get("title", "Unknown")
        overview = r.get("overview", "No description available")
        rating = r.get("vote_average", 0)
        genres = ", ".join([g["name"] for g in r.get("genres", [])])
        adult = "18+" if r.get("adult") else "Family Safe"
        actors = ", ".join([a["name"] for a in c.get("cast", [])[:5]])
        link = f"https://www.themoviedb.org/movie/{movie_id}"

        return title, overview, rating, genres, adult, actors, link
    except:
        return "Unknown", "", 0, "", "", "", ""

def login_page():
    st.title("🎬 WatchNext")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if create_user(u, p):
                st.success("Account created")
            else:
                st.error("User exists")

def app():
    now = datetime.now()

    st.markdown(f"""
    # 🎬 WatchNext
    ### {now.strftime('%A, %d %B %Y')}
    """)

    st.sidebar.success("Logged in: " + st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        genre = st.selectbox("Filter genre", ["All"] + sorted(set(movies["tags"].dropna())))

        filtered = movies if genre == "All" else movies[movies["tags"] == genre]

        movie = st.selectbox("Pick movie", filtered["title"].values)

        if st.button("Recommend"):
            recs = hybrid_recommend(movie, movies)

            cols = st.columns(5)

            for i, (idx, _) in enumerate(recs):
                if i < len(cols):
                    with cols[i]:
                        movie_id = movies.iloc[int(idx)]["id"]

                        poster = fetch_poster(movie_id)
                        title, overview, rating, genres, adult, actors, link = movie_details(movie_id)

                        st.image(poster, use_container_width=True)
                        st.markdown(f"### {title}")
                        st.write(f"⭐ {rating}")
                        st.write(f"🎭 {genres}")
                        st.write(f"👥 {actors}")
                        st.write(f"🔞 {adult}")
                        st.write(overview[:180] + "...")
                        st.markdown(f"[Open on TMDB]({link})")

            log_watch(st.session_state.user, movie)

    with tab2:
        trend = trending_movies()
        cols = st.columns(4)

        for i in range(min(4, len(trend))):
            with cols[i]:
                movie_id = trend.iloc[i]["id"]
                title, overview, rating, genres, adult, actors, link = movie_details(movie_id)

                st.image(fetch_poster(movie_id), use_container_width=True)
                st.markdown(f"**{title}**")
                st.write(f"⭐ {rating} | {genres}")
                st.write(adult)

    with tab3:
        history = get_history(st.session_state.user)

        if not history:
            st.write("No history yet")
        else:
            for h in reversed(history):
                st.write("• " + h)

    st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background: black;
        color: white;
    }
    </style>
    <div class="footer">
    ⭐💛 Designed by CHIRAG NAGPAL © 2026 — All rights reserved
    </div>
    """, unsafe_allow_html=True)

if st.session_state.user is None:
    login_page()
else:
    app()