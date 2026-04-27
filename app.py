import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from auth import create_user, login_user
from analytics import log_watch, get_history
from recommender import hybrid_recommend, trending_movies

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

st.set_page_config(page_title="WatchNext", layout="wide")

def poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        p = data.get("poster_path")
        if p:
            return "https://image.tmdb.org/t/p/w500" + p
    except:
        pass
    return PLACEHOLDER

def movie_meta(movie):
    row = movies[movies["title"] == movie].iloc[0]
    genres = row.get("tags", "Unknown")
    return genres

if "user" not in st.session_state:
    st.session_state.user = None

now = datetime.now()

st.markdown(f"""
# 🎬 WatchNext
### {now.strftime('%A, %d %B %Y')}
""")

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Account", menu)

if choice == "Signup":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Create"):
        if create_user(u, p):
            st.success("Account created")
        else:
            st.error("User exists")

elif choice == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(u, p):
            st.session_state.user = u
            st.success("Welcome " + u)
            st.rerun()
        else:
            st.error("Invalid credentials")

if st.session_state.user:

    st.sidebar.success("Logged in as " + st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        genre = st.selectbox("Filter by genre", ["All"] + list(set(movies["tags"].dropna())))

        filtered = movies if genre == "All" else movies[movies["tags"] == genre]

        movie = st.selectbox("Pick a movie", filtered["title"].values)

        if st.button("Get Recommendations"):
            recs, data = hybrid_recommend(movie, movies)

            cols = st.columns(5)

            for i in range(len(recs)):
                with cols[i]:
                    st.image(poster(movies.iloc[recs[i][0]]["id"]))
                    st.caption(movies.iloc[recs[i][0]]["title"])

            log_watch(st.session_state.user, movie)

    with tab2:
        trend = trending_movies(movies)

        cols = st.columns(4)

        for i in range(4):
            with cols[i]:
                st.image(poster(trend.iloc[i]["id"]))
                st.caption(trend.iloc[i]["title"])

    with tab3:
        history = get_history(st.session_state.user)

        if not history:
            st.write("No history yet")
        else:
            for h in reversed(history):
                st.write("• " + h)

st.markdown("""
---
⭐💛 Designed by CHIRAG NAGPAL, 2026 — All rights reserved
""")