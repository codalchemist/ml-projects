import streamlit as st
import pickle
import pandas as pd
import requests
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(movies['tags'].fillna('')).toarray()
similarity = cosine_similarity(vector)

if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(2):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            return PLACEHOLDER
        except:
            time.sleep(1)

    return PLACEHOLDER


def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]

    scores = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recs = []
    posters = []

    for i in scores:
        recs.append(movies.iloc[i[0]]['title'])
        posters.append(fetch_poster(movies.iloc[i[0]]['id']))

    return recs, posters


def hybrid_recommend(movie):
    recs, posters = recommend(movie)

    trending = movies.sample(5)

    return recs, posters, trending


st.title("🎬 CineMatch AI")

if st.session_state.user is None:
    user = st.text_input("Enter your name")
    if st.button("Enter"):
        st.session_state.user = user
        st.success("Welcome " + user)
        st.rerun()
else:
    st.sidebar.title("User")
    st.sidebar.write(st.session_state.user)

    movie = st.selectbox("Pick a movie", movies['title'].values)

    if st.button("Recommend"):
        recs, posters, trending = hybrid_recommend(movie)

        st.subheader("Because you watched")
        cols = st.columns(5)

        for i in range(len(recs)):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.caption(recs[i])

        st.session_state.history.append(movie)

        st.subheader("Trending now")
        cols = st.columns(5)

        for i, row in enumerate(trending.iterrows()):
            with cols[i]:
                st.image(fetch_poster(row[1]['id']), use_container_width=True)
                st.caption(row[1]['title'])

    if st.session_state.history:
        st.subheader("Your Watch History")
        st.write(st.session_state.history)