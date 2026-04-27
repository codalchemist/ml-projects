import streamlit as st
import requests
from datetime import datetime
import pytz
from recommender import hybrid_recommend, movies, trending_movies
from auth import create_user, login_user
from analytics import log_watch, get_history

st.set_page_config(page_title="WatchNext", layout="wide")

API_KEY = "3ee5dc1f74f34381d2b2a0e6b783a3"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

st.markdown("""
<style>
.stApp {
    background-color: #0b0b0b;
    color: #ffffff;
    font-family: "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding: 2rem 3rem 6rem 3rem;
}

h1 {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
}

h2, h3 {
    font-weight: 700;
}

div[data-testid="stImage"] img {
    border-radius: 14px;
    transition: 0.25s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.05);
}

.stTabs [data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 600;
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #0b0b0b;
    text-align: center;
    padding: 10px;
    color: #888;
    border-top: 1px solid #222;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 WatchNext</h1>", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None
if "welcome" not in st.session_state:
    st.session_state.welcome = False


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except:
        pass
    return PLACEHOLDER


def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
        return requests.get(url, timeout=8).json()
    except:
        return {}


def get_location():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=3).json()
        city = r.get("city", "Unknown")
        country = r.get("country", "IN")
        return city, country
    except:
        return "India", "IN"


def get_time():
    try:
        tz = pytz.timezone("Asia/Kolkata")
        return datetime.now(tz).strftime("%d %b %Y • %H:%M")
    except:
        return datetime.now().strftime("%d %b %Y • %H:%M")


def get_weather():
    try:
        r = requests.get("https://wttr.in/?format=%t", timeout=3).text.strip()
        if "F" in r:
            f = float(r.replace("°F", "").replace("F", ""))
            c = round((f - 32) * 5 / 9)
            return f"{c}°C"
        return r.replace("+", "").replace("Â", "")
    except:
        return "N/A"


def filter_by_genre(df, genre):
    if genre == "All":
        return df
    return df[df["tags"].str.contains(genre.lower(), na=False)]


if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username", key="lu")
        p = st.text_input("Password", type="password", key="lp")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.session_state.welcome = True
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username", key="su")
        p = st.text_input("New Password", type="password", key="sp")

        if st.button("Signup"):
            if create_user(u, p):
                st.success("Account created")
            else:
                st.error("User already exists")

else:

    city, country = get_location()

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success(st.session_state.user)

    st.sidebar.markdown("### 🌍 Context")
    st.sidebar.write(f"📍 {city}, {country}")
    st.sidebar.write(f"🕒 {get_time()}")
    st.sidebar.write(f"🌡️ {get_weather()}")

    if st.session_state.welcome:
        st.session_state.welcome = False
        st.success(f"🎬 Welcome {st.session_state.user} — WatchNext is ready!")

    tab1, tab2, tab3 = st.tabs(["🎯 For You", "🍿 Trending", "📊 History"])

    with tab1:

        genre = st.selectbox("Select Genre", ["All", "Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"])

        filtered = filter_by_genre(movies, genre)

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

                    st.markdown(f"**{df.iloc[idx]['title']}**")

                    st.write(details.get("overview", "No description available")[:160] + "...")

                    st.write("⭐", details.get("vote_average", "N/A"))

                    if details.get("homepage"):
                        st.link_button("🎬 Watch / Info", details["homepage"])
                    else:
                        st.link_button(
                            "🔗 TMDB",
                            f"https://www.themoviedb.org/movie/{df.iloc[idx]['id']}"
                        )

    with tab2:

        st.subheader("🍿 Trending Movies")

        top = trending_movies()
        cols = st.columns(4)

        for i in range(min(len(top), 8)):

            details = fetch_details(top.iloc[i]["id"])

            with cols[i % 4]:

                st.image(fetch_poster(top.iloc[i]["id"]))

                st.markdown(f"**{top.iloc[i]['title']}**")

                cast = details.get("credits", {}).get("cast", [])[:3]
                actors = ", ".join([a["name"] for a in cast]) if cast else "N/A"

                st.write("🎭", actors)
                st.write("⭐", details.get("vote_average", "N/A"))

                with st.expander("Overview"):
                    st.write(details.get("overview", "No description"))

    with tab3:

        st.subheader("📊 Watch History")

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