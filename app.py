import streamlit as st
import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "3ee5dc2f1f74f34382d1b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

movies = pd.DataFrame(pd.read_pickle("movie_dict.pkl"))

if "tags" not in movies.columns:
    st.error("Dataset missing 'tags' column")
    st.stop()

cv = CountVectorizer(max_features=5000, stop_words="english")
vector = cv.fit_transform(movies["tags"].fillna(""))
similarity = cosine_similarity(vector)


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

        r = requests.get(url, timeout=8)
        c = requests.get(c_url, timeout=8)

        if r.status_code != 200:
            return None

        r = r.json()
        c = c.json()

        title = r.get("title", "Unknown")
        overview = r.get("overview", "No description available")
        rating = r.get("vote_average", 0)

        genres = ", ".join([g["name"] for g in r.get("genres", [])]) or "N/A"
        actors = ", ".join([a["name"] for a in c.get("cast", [])[:5]]) or "N/A"

        adult = "18+" if r.get("adult") else "Family Safe"
        link = f"https://www.themoviedb.org/movie/{movie_id}"

        return title, overview, rating, genres, actors, adult, link

    except:
        return None


def recommend(movie):
    if movie not in movies["title"].values:
        return []

    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]

    return scores


st.title("🎬 WatchNext")

movie = st.selectbox("Pick a movie", movies["title"].values)

if st.button("Recommend"):

    recs = recommend(movie)
    cols = st.columns(5)

    for i, (idx, _) in enumerate(recs):
        with cols[i]:

            movie_id = movies.iloc[idx]["id"]

            poster = fetch_poster(movie_id)
            details = movie_details(movie_id)

            if details:
                title, overview, rating, genres, actors, adult, link = details

                st.image(poster, use_container_width=True)

                st.markdown(f"### {title}")
                st.write(f"⭐ Rating: {rating}")
                st.write(f"🎭 Genres: {genres}")
                st.write(f"👥 Actors: {actors}")
                st.write(f"🔞 {adult}")
                st.write(overview[:200] + "...")
                st.markdown(f"[🎬 View on TMDB]({link})")


st.markdown("---")
st.markdown("⭐💛 Designed by CHIRAG NAGPAL © 2026 — All rights reserved")