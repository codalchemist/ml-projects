import streamlit as st
import pickle
import pandas as pd
import requests
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

cv = CountVectorizer(max_features=5000, stop_words="english")
vector = cv.fit_transform(movies["tags"].fillna("")).toarray()
similarity = cosine_similarity(vector)

if "user" not in st.session_state:
    st.session_state.user = ""
if "history" not in st.session_state:
    st.session_state.history = []

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    for _ in range(2):
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            p = data.get("poster_path")
            if p:
                return "https://image.tmdb.org/t/p/w500" + p
            return PLACEHOLDER
        except:
            time.sleep(1)
    return PLACEHOLDER

def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:8]

    names = []
    posters = []

    for i in scores:
        names.append(movies.iloc[i[0]]["title"])
        posters.append(fetch_poster(movies.iloc[i[0]]["id"]))

    return names, posters

def trending_movies():
    return movies.sample(8)

st.set_page_config(page_title="CineMatch AI", layout="wide")

st.title("🎬 CineMatch AI")

if not st.session_state.user:
    name = st.text_input("Enter your name")
    if st.button("Start"):
        st.session_state.user = name
        st.rerun()
else:
    st.sidebar.write("User: " + st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Recommend"):
            names, posters = recommend(movie)
            st.session_state.history.append(movie)

            cols = st.columns(5)

            for i in range(5):
                with cols[i]:
                    st.image(posters[i], use_container_width=True)
                    st.caption(names[i])

    with tab2:
        trend = trending_movies()
        cols = st.columns(4)

        for i in range(4):
            with cols[i]:
                st.image(fetch_poster(trend.iloc[i]["id"]), use_container_width=True)
                st.caption(trend.iloc[i]["title"])

    with tab3:
        if len(st.session_state.history) == 0:
            st.write("No history yet")
        else:
            for m in reversed(st.session_state.history):
                st.write("• " + m)