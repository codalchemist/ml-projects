import streamlit as st
import requests
from datetime import datetime
from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user
from analytics import log_watch, get_history

API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.set_page_config(page_title="WatchNext", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0b0b0b;
    color: white;
}

.block-container {
    padding: 2rem 3rem 6rem 3rem;
}

h1 {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
}

div[data-testid="stImage"] img {
    border-radius: 14px;
    transition: transform 0.25s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.05);
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #0b0b0b;
    text-align: center;
    color: #aaa;
    padding: 10px;
    font-size: 12px;
    border-top: 1px solid #222;
}
.card {
    background: #111;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 WatchNext</h1>", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url, timeout=10).json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except:
        pass
    return PLACEHOLDER


def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
        return requests.get(url, timeout=10).json()
    except:
        return {}


def get_weather():
    try:
        r = requests.get("https://wttr.in/Delhi?format=%t", timeout=3)
        temp = r.text.strip()
        return temp.replace("+", "").replace("Â", "")
    except:
        return "N/A"


def filter_by_genre(df, genre):
    if genre == "All":
        return df
    if "genres" not in df.columns:
        return df
    return df[df["genres"].astype(str).str.contains(genre, case=False, na=False)]


if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("Username", key="sign_u")
        p = st.text_input("Password", type="password", key="sign_p")

        if st.button("Signup"):
            if create_user(u, p):
                st.success("Account created")
            else:
                st.error("User already exists")

else:

    time_now = datetime.now().strftime("%A • %H:%M")
    temp = get_weather()

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success(st.session_state.user)

    st.sidebar.markdown("### 🌍 Context")
    st.sidebar.write("🕒", time_now)
    st.sidebar.write("🌡️", temp + "°C")

    tab1, tab2, tab3 = st.tabs(["For You", "🍿 Trending", "History"])

    with tab1:

        genre = st.selectbox(
            "Choose Genre",
            ["All", "Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"]
        )

        filtered_movies = filter_by_genre(movies, genre)

        movie = st.selectbox("Pick a movie", filtered_movies["title"].values)

        if st.button("Get Recommendations"):

            recs, df = hybrid_recommend(movie)
            log_watch(st.session_state.user, movie)

            cols = st.columns(min(5, len(recs)))

            for i, (idx, score) in enumerate(recs[:5]):

                details = fetch_details(df.iloc[idx]["id"])

                with cols[i]:

                    st.image(fetch_poster(df.iloc[idx]["id"]))

                    st.markdown(f"**{df.iloc[idx]['title']}**")

                    st.write(details.get("overview", "No description")[:140] + "...")

                    st.write("⭐", details.get("vote_average", "N/A"))

                    if details.get("homepage"):
                        st.link_button("▶ Watch / Info", details["homepage"])
                    else:
                        st.link_button(
                            "▶ TMDB Page",
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
                actors = ", ".join([a["name"] for a in cast]) if cast else "N/A"

                st.write("🎭", actors)
                st.write("⭐", details.get("vote_average", "N/A"))

                with st.expander("More info"):
                    st.write(details.get("overview", "No description available"))

    with tab3:

        st.subheader("📊 Watch History")

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