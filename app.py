import streamlit as st
import requests
from datetime import datetime
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
    padding-bottom: 5rem;
}

h1, h2, h3 {
    color: white;
}

div[data-testid="stImage"] img {
    border-radius: 14px;
    transition: transform 0.25s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.07);
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #0b0b0b;
    text-align: center;
    color: gray;
    padding: 8px;
    font-size: 12px;
    border-top: 1px solid #222;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align:center;'>🎬 WatchNext</h1>", unsafe_allow_html=True)


API_KEY = "3ee5dc2f1f74f34381d2b2a0e6b783a3"


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
    return "https://via.placeholder.com/500x750?text=No+Poster"


def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
        return requests.get(url, timeout=10).json()
    except:
        return {}


def get_weather():
    try:
        r = requests.get("https://wttr.in/?format=%t", timeout=3)
        return r.text.strip()
    except:
        return "N/A"


def extract_genres(movie):
    return movie.get("genres", [])


if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.rerun()

    with tab2:
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):
            if create_user(new_user, new_pass):
                st.success("Account created")


else:

    weather = get_weather()
    time_now = datetime.now().strftime("%A • %H:%M")

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success(st.session_state.user)

    st.sidebar.markdown("### 🌍 Context")
    st.sidebar.write("🕒", time_now)
    st.sidebar.write("🌡️", weather + "°C")


    tab1, tab2, tab3 = st.tabs(["For You", "Popcorn Trending 🍿", "History"])


    with tab1:

        st.subheader("🎯 Tell us your taste")

        genre = st.selectbox(
            "Select Genre",
            ["All", "Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"]
        )

        movie = st.selectbox("Pick a movie", movies["title"].values)

        if st.button("Get Recommendations"):

            recs, df = hybrid_recommend(movie)

            log_watch(st.session_state.user, movie)

            cols = st.columns(min(5, len(recs)))

            for i, (idx, score) in enumerate(recs[:5]):

                details = fetch_details(df.iloc[idx]["id"])

                with cols[i]:

                    st.image(fetch_poster(df.iloc[idx]["id"]), use_container_width=True)

                    st.markdown("**" + df.iloc[idx]["title"] + "**")

                    st.write(details.get("overview", "No description available")[:120] + "...")

                    rating = details.get("vote_average", "N/A")
                    adult = "🔞 Adult" if details.get("adult") else "👨‍👩‍👧 Family Safe"

                    st.write(f"⭐ Rating: {rating}")
                    st.write(adult)

                    genres = [g["name"] for g in details.get("genres", [])]
                    st.write("🎭 Genres:", ", ".join(genres))

                    if details.get("homepage"):
                        st.link_button("🎬 Watch / Info", details["homepage"])


    with tab2:

        st.subheader("🍿 Trending Now")

        top = trending_movies()
        cols = st.columns(4)

        for i in range(len(top)):
            details = fetch_details(top.iloc[i]["id"])

            with cols[i % 4]:

                st.image(fetch_poster(top.iloc[i]["id"]), use_container_width=True)

                st.markdown("**" + top.iloc[i]["title"] + "**")

                actors = details.get("credits", {}).get("cast", [])[:3]
                actor_names = [a["name"] for a in actors]

                st.write("🎭 Actors:", ", ".join(actor_names))

                st.write("⭐", details.get("vote_average", "N/A"))


    with tab3:

        st.subheader("📊 Your Watch History")

        history = get_history(st.session_state.user)

        if history:
            for m in reversed(history[-10:]):
                st.write("•", m)
        else:
            st.write("No watch history yet")


st.markdown("""
<div class="footer">
⭐💛 Built by Chirag Nagpal • WatchNext © 2026 • All Rights Reserved
</div>
""", unsafe_allow_html=True)