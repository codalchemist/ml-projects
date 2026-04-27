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

    pop_weight = 0.3
    content_weight = 0.7

    scores = []

    for i, score in content_scores:
        popularity = movies.iloc[i]["vote_average"] if "vote_average" in movies.columns else 1
        final = (content_weight * score) + (pop_weight * popularity)
        scores.append((i, final))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:8]

    return scores, movies


def trending_movies():
    if "vote_average" in movies.columns:
        return movies.sort_values("vote_average", ascending=False).head(8)

    if "popularity" in movies.columns:
        return movies.sort_values("popularity", ascending=False).head(8)

    return movies.sample(8)