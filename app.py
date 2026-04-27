import streamlit as st
import requests
from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user
from analytics import log_watch, get_history


st.set_page_config(page_title="WatchNext", layout="wide")


st.markdown("""
<style>
.stApp {
    background-color: #0b0b0b;
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

h1, h2, h3 {
    color: white;
}

div[data-testid="stImage"] img {
    border-radius: 12px;
    transition: transform 0.25s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.07);
}

.css-1v0mbdj {
    gap: 1.2rem;
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    "<h1 style='text-align:center; margin-bottom:20px;'>🎬 WatchNext</h1>",
    unsafe_allow_html=True
)


if "user" not in st.session_state:
    st.session_state.user = None


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3ee5dc2f1f74f34381d2b2a0e6b783a3"
        data = requests.get(url, timeout=10).json()
        path = data.get("poster_path")
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"


if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Create Account")

        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):
            if create_user(new_user, new_pass):
                st.success("Account created")
            else:
                st.error("User already exists")

else:

    st.sidebar.write("👤 User:", st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "History"])

    with tab1:
        st.subheader("🎯 Recommended for you")

        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Get Recommendations"):
            recs, df = hybrid_recommend(movie)

            log_watch(st.session_state.user, movie)

            cols = st.columns(5)

            for i, (idx, score) in enumerate(recs):
                with cols[i]:
                    st.image(fetch_poster(df.iloc[idx]["id"]), use_container_width=True)
                    st.caption(df.iloc[idx]["title"])

    with tab2:
        st.subheader("🔥 Trending Now")

        top = trending_movies()
        cols = st.columns(4)

        for i in range(len(top)):
            with cols[i % 4]:
                st.image(fetch_poster(top.iloc[i]["id"]), use_container_width=True)
                st.caption(top.iloc[i]["title"])

    with tab3:
        st.subheader("📊 Your Watch History")

        history = get_history(st.session_state.user)

        if history:
            for m in reversed(history[-10:]):
                st.write("•", m)
        else:
            st.write("No watch history yet")