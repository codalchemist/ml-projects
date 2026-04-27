import streamlit as st
import requests
from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user
from analytics import log_watch, get_history

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        data = requests.get(url, timeout=10).json()
        path = data.get("poster_path")
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except:
        pass
    return PLACEHOLDER


st.markdown("""
<style>
.stApp {
    background-color: #0e0e0e;
    color: white;
}
div[data-testid="stImage"] img {
    border-radius: 12px;
    transition: transform 0.2s;
}
div[data-testid="stImage"] img:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 WatchNext")

if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()

    with tab2:
        u = st.text_input("Username", key="signup_u")
        p = st.text_input("Password", type="password", key="signup_p")

        if st.button("Signup"):
            if create_user(u, p):
                st.success("Account created")

else:

    st.sidebar.write("Logged in as:", st.session_state.user)

    tab1, tab2, tab3 = st.tabs(["For You", "Trending", "Insights"])

    with tab1:
        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Recommend"):
            recs, df = hybrid_recommend(movie)

            log_watch(st.session_state.user, movie)

            st.subheader("Because you watched " + movie)

            cols = st.columns(5)

            for i, (idx, score) in enumerate(recs):
                with cols[i]:
                    st.image(fetch_poster(df.iloc[idx]["id"]))
                    st.caption(df.iloc[idx]["title"])

    with tab2:
        st.subheader("Trending Now")

        top = trending_movies()
        cols = st.columns(4)

        for i in range(len(top)):
            with cols[i % 4]:
                st.image(fetch_poster(top.iloc[i]["id"]))
                st.caption(top.iloc[i]["title"])

    with tab3:
        st.subheader("Your Taste Profile")

        history = get_history(st.session_state.user)

        if history:
            st.write("Movies watched:", len(history))
            st.write("Recent:", history[-10:])
        else:
            st.write("No activity yet")