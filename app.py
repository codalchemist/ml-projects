import streamlit as st
import requests
from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        path = data.get("poster_path")

        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except:
        pass

    return PLACEHOLDER


st.title("🎬 WatchNext")

if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):
            if create_user(new_user, new_pass):
                st.success("Account created")
            else:
                st.error("User already exists")

else:

    st.sidebar.write("User:", st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Recommend"):
            recs, df = hybrid_recommend(movie)

            st.session_state.history.append(movie)

            st.subheader(f"Because you watched {movie}")

            cols = st.columns(5)

            for i, (idx, score) in enumerate(recs):
                with cols[i]:
                    st.image(fetch_poster(df.iloc[idx]["id"]), use_container_width=True)
                    st.caption(df.iloc[idx]["title"])

    with tab2:
        st.subheader("Trending Movies")

        top = trending_movies()

        cols = st.columns(4)

        for i in range(min(4, len(top))):
            with cols[i]:
                st.image(fetch_poster(top.iloc[i]["id"]), use_container_width=True)
                st.caption(top.iloc[i]["title"])

    with tab3:
        st.subheader("Watch History")

        if st.session_state.history:
            for m in reversed(st.session_state.history):
                st.write("• " + m)
        else:
            st.write("No history yet")