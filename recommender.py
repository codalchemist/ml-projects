import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

cv = CountVectorizer(max_features=5000, stop_words="english")
vector = cv.fit_transform(movies["tags"].fillna("")).toarray()
similarity = cosine_similarity(vector)


def hybrid_recommend(movie):
    idx = movies[movies["title"] == movie].index[0]

    content_scores = list(enumerate(similarity[idx]))

    pop_series = None
    if "vote_average" in movies.columns:
        pop_series = movies["vote_average"]
    elif "popularity" in movies.columns:
        pop_series = movies["popularity"]
    else:
        pop_series = pd.Series([1] * len(movies))

    final_scores = []

    for i, score in content_scores:
        pop = pop_series.iloc[i]
        final_scores.append((i, score * 0.7 + pop * 0.3))

    final_scores = sorted(final_scores, key=lambda x: x[1], reverse=True)[1:8]

    return final_scores, movies


def trending_movies():
    if "vote_average" in movies.columns:
        return movies.sort_values("vote_average", ascending=False).head(8)

    if "popularity" in movies.columns:
        return movies.sort_values("popularity", ascending=False).head(8)

    return movies.sample(8)