from os import environ
import requests
from MyMovieApp.models import Movies
from MyMovieApp import db

#loads data from API into db
def load_data():
    results = []
    for gn in [1,3,7,6,10]:
        for num in range(1,4):
            url = "https://api.themoviedb.org/4/list/{}?page={}".format(gn, num)
            query_params = {'api_key':environ.get('API_KEY')}
            data = requests.get(url, params=query_params)
            datum = data.json()
            det = datum['results']
            results += det
    print(len(results))
    for films in results:
        if not Movies.query.filter_by(title=films['title']).first():
            new_movie = Movies(
            title=films.get('title'),
            rated_18=films.get('adult'),
            overview=films.get('overview'),
            popularity=films.get('popularity'),
            release_date=films.get('release_date', 'not available'),
            vote_average=films.get('vote_average')
            )
            db.session.add(new_movie)
            db.session.commit()

    return 'Done'



load_data()
