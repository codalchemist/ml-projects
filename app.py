import streamlit as st
import requests
from datetime import datetime

from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user
from analytics import log_watch, get_history


st.set_page_config(page_title="WatchNext", layout="wide")

API_KEY = "3ee5dc1f74f34381d2b2a0e6b783a3"
POSTER_FALLBACK = "https://via.placeholder.com/500x750?text=No+Poster"


st.markdown("""
<style>
.stApp {
    background-color: #0b0b0b;
    color: #f5f5f5;
    font-family: Helvetica, Arial, sans-serif;
}

h1 {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 10px;
}

.block-container {
    padding: 2rem 3rem;
}

div[data-testid="stImage"] img {
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    background: #0b0b0b;
    color: #777;
    font-size: 12px;
    padding: 8px;
    border-top: 1px solid #222;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 WatchNext</h1>", unsafe_allow_html=True)

#
if "user" not in st.session_state:
    st.session_state.user = None


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        data = requests.get(url, timeout=5).json()
        path = data.get("poster_path")
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except:
        pass
    return POSTER_FALLBACK


def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
        return requests.get(url, timeout=5).json()
    except:
        return {}


def safe(val):
    return val if val else "Not available"



if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if create_user(u, p):
                st.success("Account created")


else:

    st.sidebar.success(f"👤 {st.session_state.user}")
    st.sidebar.write("🕒", datetime.now().strftime("%d %b %Y • %H:%M"))
    st.sidebar.write("🌍 India 🇮🇳")

    tab1, tab2, tab3 = st.tabs(["🎯 For You", "🍿 Trending", "📊 History"])

    # ---------------- FOR YOU ----------------
    with tab1:

        st.subheader("Choose your mood / genre")

        genre = st.selectbox(
            "Select Genre",
            ["All", "Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"]
        )

        # FIXED FILTER (NO BREAK)
        if genre == "All":
            filtered = movies
        else:
            filtered = movies[movies["tags"].str.lower().str.contains(genre.lower(), na=False)]

        movie = st.selectbox("Pick a movie", filtered["title"].values)

        if st.button("Get Recommendations"):

            recs, df = hybrid_recommend(movie)
            log_watch(st.session_state.user, movie)

            safe_len = min(5, len(recs))
            cols = st.columns(safe_len)

            for i, (idx, score) in enumerate(recs[:safe_len]):

                details = fetch_details(df.iloc[idx]["id"])

                with cols[i]:

                    st.image(fetch_poster(df.iloc[idx]["id"]))

                    st.markdown(f"### {df.iloc[idx]['title']}")

                    st.write("📖", safe(details.get("overview"))[:150] + "...")

                    st.write("⭐ Rating:", safe(details.get("vote_average")))

                    st.write("🔞 Family Safe:", "Yes" if not details.get("adult") else "No")

                    genres = ", ".join([g["name"] for g in details.get("genres", [])]) if details.get("genres") else "N/A"
                    st.write("🎭 Genres:", genres)

                    cast = details.get("credits", {}).get("cast", [])[:3]
                    actors = ", ".join([c["name"] for c in cast]) if cast else "N/A"
                    st.write("🎬 Actors:", actors)

                    st.link_button(
                        "▶ View Movie",
                        f"https://www.themoviedb.org/movie/{df.iloc[idx]['id']}"
                    )


    with tab2:

        st.subheader("🍿 Trending Movies")

        top = trending_movies()
        cols = st.columns(4)

        for i in range(min(8, len(top))):

            details = fetch_details(top.iloc[i]["id"])

            with cols[i % 4]:

                st.image(fetch_poster(top.iloc[i]["id"]))

                st.markdown(f"**{top.iloc[i]['title']}**")

                cast = details.get("credits", {}).get("cast", [])[:3]
                actors = ", ".join([c["name"] for c in cast]) if cast else "N/A"

                st.caption("🎬 " + actors)
                st.write("⭐", safe(details.get("vote_average")))

                with st.expander("Overview"):
                    st.write(safe(details.get("overview")))


    with tab3:

        st.subheader("Watch History")

        history = get_history(st.session_state.user)

        if history:
            for m in reversed(history[-10:]):
                st.write("•", m)
        else:
            st.write("No history yet")



st.markdown("""
<div class="footer">
⭐💛 Built by Chirag Nagpal • WatchNext © 2026 • All Rights Reserved
</div>
""", unsafe_allow_html=True)