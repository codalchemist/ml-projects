import streamlit as st
import pandas as pd
import requests
import time

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

if "history" not in st.session_state:
    st.session_state.history = []


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
        actors = ", ".join([a["name"] for a in credits.get("cast", [])[:5]]) or "N/A"

        adult = "🔞 18+" if data.get("adult") else "👨‍👩‍👧 Family Safe"
        link = f"https://www.themoviedb.org/movie/{movie_id}"

        poster_path = data.get("poster_path")
        poster = "https://image.tmdb.org/t/p/w500" + poster_path if poster_path else PLACEHOLDER

        return title, overview, rating, genres, actors, adult, link, poster

    except:
        return None


def recommend(movie):
    if movie not in movies["title"].values:
        return []

    idx = movies[movies["title"] == movie].index[0]

    return list(enumerate([1] * len(movies)))[1:6]


st.title("🎬 WatchNext")


movie = st.selectbox("Pick a movie", movies["title"].values)

if st.button("Get Recommendations"):

    recs = recommend(movie)

    cols = st.columns(5)

    for i, (idx, _) in enumerate(recs[:5]):

        movie_id = movies.iloc[idx]["id"]
        details = fetch_movie_details(movie_id)

        if details:
            title, overview, rating, genres, actors, adult, link, poster = details

            with cols[i]:
                st.image(poster, use_container_width=True)
                st.markdown(f"### {title}")
                st.write(f"⭐ {rating}")
                st.write(genres)
                st.write(actors)
                st.write(adult)
                st.write(overview[:180] + "...")
                st.markdown(f"[🎬 Open on TMDB]({link})")

    st.session_state.history.append(movie)


st.subheader("📜 Watch History")

for h in reversed(st.session_state.history):
    st.write("• " + h)


st.markdown("---")
st.markdown("⭐💛 Designed by CHIRAG NAGPAL © 2026 — All rights reserved")