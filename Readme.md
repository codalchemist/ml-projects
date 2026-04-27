# 🎬 WatchNext

A Netflix-inspired movie recommendation platform built to help users discover what to watch next through personalized recommendations, trending picks, and genre-based filtering.

Designed with a premium streaming-platform aesthetic and focused on delivering a clean, modern user experience.

---

## 🚀 Live Demo

[Launch WatchNext](https://ml-projects-3qf88cv5nnxfmjugtyekkz.streamlit.app/)

---

## ✨ Features

- Personalized movie recommendations based on selected titles  
- Genre / mood filtering for targeted discovery  
- Trending movies section  
- User authentication (Login / Signup)  
- Watch history tracking  
- Real-time movie metadata via TMDB API  
- Premium Netflix-style responsive UI  
- Hover animations and cinematic hero banner  

---

## 🛠 Tech Stack

- **Frontend / App Framework:** Streamlit  
- **Backend Logic:** Python  
- **Machine Learning:** Scikit-learn (Content-Based Filtering)  
- **Database:** SQLite  
- **Movie Data API:** TMDB API  
- **Styling:** Custom CSS  

---

## 🧠 Recommendation Approach

WatchNext uses a **content-based recommendation system** powered by cosine similarity.

Movie metadata such as genres, keywords, cast, and tags are vectorized using CountVectorizer, and similarity scores are computed to recommend movies related to the user's selected title.

---

## 📸 Screenshots

Screenshots will be added soon.

---

## ⚙️ Run Locally

```bash
git clone https://github.com/codalchemist/ml-projects.git
cd ml-projects
pip install -r requirements.txt
streamlit run app.py
📌 Future Improvements
Dynamic featured movie banner
Collaborative filtering recommendations
Favorites / Watchlist support
Search with autocomplete
Better trending algorithm using live TMDB trending API
Mobile-responsive enhancements
👨‍💻 Author

Chirag Nagpal

Built with attention to both functionality and product design.
## 📄 License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software in accordance with the license terms.
