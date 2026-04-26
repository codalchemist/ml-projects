import streamlit as st
import pickle
import pandas as pd
import requests
import time

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for attempt in range(3):   # Retry 3 times
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            poster_path = data.get('poster_path')

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                return "https://via.placeholder.com/500x750?text=No+Poster"

        except Exception as e:
            print(f"ERROR FOR MOVIE ID {movie_id}: {e}")
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=Failed+To+Load"
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['id']

        recommended_movies.append(
            movies.iloc[i[0]]['title']
        )

        recommended_movies_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_movies_posters


st.title("🎬 Movie Recommender")
st.write("Discover similar movies instantly.")

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values
)

if st.button('Get Recommendations'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            if posters[i]:
                st.image(posters[i])
            st.caption(names[i])