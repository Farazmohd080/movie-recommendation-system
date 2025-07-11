from flask import Flask, render_template, request
import pickle
import requests
import os
from io import BytesIO

app = Flask(__name__)

# Load data
movie_url = "https://www.dropbox.com/scl/fi/88rsvvc4arto8kozuvl1a/movie_rec.pkl?rlkey=nfia4d10ci414m9euns850gac&st=5rurtwia&dl=1"
response1 = requests.get(movie_url)
movies = pickle.load(BytesIO(response1.content))

# Load similarity matrix
similarity_url = "https://www.dropbox.com/scl/fi/qw9qtciicxhd7rulrm8ac/similarity.pkl?rlkey=8j3dj22p6uivwrfdgn3e1wibg&st=6wg6tpkw&dl=1"
response = requests.get(similarity_url)
similarity = pickle.load(BytesIO(response.content))
# Function to fetch movie poster from OMDb using movie title

import urllib.parse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def fetch_poster(movie_title):
    api_key = "ea94c1af8f575c0b1db18acc327c19d3"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    
    try:
        response = session.get(url, timeout=5)
        data = response.json()
        poster_path = data['results'][0].get("poster_path", "")
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request failed: {e}")
        return None


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    movies_list = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:21]
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_title=movies.iloc[i[0]].title
        recommended_movie_names.append(movie_title)
        recommended_movie_posters.append(fetch_poster(movie_title))
    return recommended_movie_names, recommended_movie_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_list = movies['title'].values
    recommendations = []
    posters = []

    if request.method == 'POST':
        selected_movie = request.form.get('movie_name')
        recommendations, posters = recommend(selected_movie)

    return render_template('index.html', movie_list=movie_list, recommendations=zip(recommendations, posters))

if __name__ == '__main__':
    app.run(debug=True)
