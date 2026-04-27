import os
import streamlit as st
import pandas as pd
import requests
import time
from recommender import recommend
from analytics import log_watch, get_history
from auth import create_user, login_user

API_KEY = st.secrets.get("3ee5dc2f1f74f34381d2b2a0e6b783a3") or os.getenv("3ee5dc2f1f74f34381d2b2a0e6b783a3")
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

if not API_KEY:
    st.error("Missing TMDB API Key")
    st.stop()

def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        credits_url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}/credits?api_key={API_KEY}"

        r = requests.get(url, timeout=8)
        c = requests.get(credits_url, timeout=8)

        if r.status_code != 200:
            return None

        data = r.json()
        credits = c.json() if c.status_code == 200 else {}

        title = data.get("title", "Unknown")
        overview = data.get("overview", "No description available")
        rating = data.get("vote_average", 0)
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "N/A"
        adult = "🔞 18+" if data.get("adult") else "👨‍👩‍👧 Family Safe"
        actors = ", ".join([a["name"] for a in credits.get("cast", [])[:5]]) or "N/A"
        link = f"https://www.themoviedb.org/movie/{movie_id}"

        poster_path = data.get("poster_path")
        poster = "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else PLACEHOLDER

        return title, overview, rating, genres, actors, adult, link, poster

    except:
        return None


def get_recommendations(movie):
    try:
        recs = recommend(movie)
        return recs
    except:
        return []


if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []


st.title("🎬 WatchNext")


if not st.session_state.user:
    st.sidebar.subheader("Login / Signup")

    option = st.sidebar.selectbox("Choose", ["Login", "Signup"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if option == "Signup":
        if st.sidebar.button("Create Account"):
            if create_user(username, password):
                st.sidebar.success("Account created")
            else:
                st.sidebar.error("User already exists")

    if option == "Login":
        if st.sidebar.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.sidebar.error("Invalid login")

else:

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Recommend"):
            recs = get_recommendations(movie)

            cols = st.columns(5)

            for i, (idx, _) in enumerate(recs):
                if i >= 5:
                    break

                movie_id = movies.iloc[idx]["id"]
                details = fetch_movie_details(movie_id)

                if details:
                    title, overview, rating, genres, actors, adult, link, poster = details

                    with cols[i]:
                        st.image(poster, use_container_width=True)
                        st.markdown(f"### {title}")
                        st.write(f"⭐ {rating}")
                        st.write(f"{genres}")
                        st.write(f"{actors}")
                        st.write(adult)
                        st.write(overview[:180] + "...")
                        st.markdown(f"[Open on TMDB]({link})")

            st.session_state.history.append(movie)
            log_watch(st.session_state.user, movie)

    with tab2:
        st.subheader("Trending Movies")

        sample = movies.sample(5)

        cols = st.columns(5)

        for i in range(5):
            m = sample.iloc[i]
            details = fetch_movie_details(m["id"])

            if details:
                title, overview, rating, genres, actors, adult, link, poster = details

                with cols[i]:
                    st.image(poster, use_container_width=True)
                    st.caption(title)

    with tab3:
        st.subheader("Watch History")

        history = get_history(st.session_state.user)

        if not history:
            st.write("No history yet")
        else:
            for h in reversed(history):
                st.write("• " + h)


st.markdown("---")
st.markdown("⭐💛 Designed by CHIRAG NAGPAL © 2026 — All rights reserved")