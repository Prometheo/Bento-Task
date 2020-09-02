from flask import current_app as app, make_response, request, json, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, token_required, Movies, PersonalRating
from . import db



@app.route('/', methods=['GET'])
def home():
    print('getting docs')
    return render_template('swaggerui.html')

@app.route('/api/swagger', methods=['GET'])
def docs():
    print('getting docs')
    return render_template('swaggerui.html')

@app.route('/api/movies', methods=['GET', 'POST'])
@token_required
def list_add_movies(current_user):
    if request.method == 'GET':
        movies = Movies.query.all()
        return jsonify([movie.serializer for movie in movies])
    elif request.method == 'POST':
        data = request.data
        data_dict = json.loads(data)

        movie = data_dict.get('title', '')
        rating = data_dict.get('rating', '')
        comment = data_dict.get('comments', '')

        print(rating)
        if not (movie and rating):
            res = {'message':'please make sure you give a rating and movie title'}
            return make_response(jsonify(res)), 400
        if rating > 10:
            res = {'message':'rating is based on a scale of 1-10'}
            return make_response(jsonify(res)), 400
        movie_to_add = Movies.query.filter_by(title=movie).first()
        print(movie_to_add)
        if movie_to_add:
            if movie_to_add in current_user.movies_list:
                res = {'message':"you already added this movie to your favorite, you really like this movie don't you?"}
                return make_response(jsonify(res)), 200
            
            try:
                user_list = PersonalRating(
                user_id=current_user.id,
                movies_id=movie_to_add.id,
                my_rating=rating,
                my_comment=comment
                )
                db.session.add(user_list)
                db.session.commit()
                res = {'message':'movie successfully added to your list'}
                return make_response(jsonify(res)), 201
            except:
                res = {'message': 'failed to add movie, please check your inputs and try again'}
                return make_response(jsonify(res)), 400
        res = {'message': 'The movie you are trying to add does not exist'}
        return make_response(jsonify(res)), 404


@app.route('/api/my_movies', methods=['GET'])
@token_required
def list_movie(current_user):
    def serialize(obj):
        title = obj.title
        movi_id = obj.id
        user = current_user
        info = PersonalRating.query.filter_by(user_id=current_user.id).filter_by(movies_id=obj.id).first()
        my_rating = info.my_rating
        my_comment = info.my_comment
        return {
            'movie title': title,
            'my rating': my_rating,
            'my comment': my_comment,
            'id': movi_id
        }
    lst = current_user.movies_list 
    return jsonify([serialize(movie) for movie in lst])

@app.route('/api/my_movies/<movie_id>', methods=['PUT','DELETE'])
@token_required
def update_delete_movie(current_user, movie_id):
    try:
        movie_info = PersonalRating.query.filter_by(user_id=current_user.id).filter_by(movies_id=movie_id).first()
    except:
        res = {'message': 'Movie with that id does not exist on your list'}
        return make_response(jsonify(res)), 400
    data = request.data
    print(movie_info)
    data_dict = json.loads(data)
    rating = data_dict.get('rating')
    comment = data_dict.get('comment')
    if request.method == 'PUT':
        if rating:
            movie_info.my_rating = rating
        if comment:
            movie_info.my_comment = comment
        try:
            db.session.add(movie_info)
            db.session.commit()
        except:
            res = {
                'message':'check your inputs and try again'
            }
            return make_response(jsonify(res)), 403
        res = {
            'message':'update made successfully'
        }
        return make_response(jsonify(res)), 201
    elif request.method == 'DELETE':
        db.session.delete(movie_info)
        db.session.commit()
        res = {'message':'movie removed from your list'}
        return make_response(jsonify(res)), 200



@app.route('/api/register', methods=['POST'])
def signup_view():
    data = request.data
    userdata_dict = json.loads(data)
    email = userdata_dict.get('email')
    username = userdata_dict.get('username')
    password = userdata_dict.get('password')

    user = User.query.filter_by(username=username).first()
    print(user)
    if user:
        res = {'Message':'User already exists'}
        return make_response(jsonify(res)), 308
    new_user = User(
        email=email,
        username=username,
        password_hash=generate_password_hash(password, 'sha256')
    )

    db.session.add(new_user)
    db.session.commit()
    res = {'messaage':'User registered successfully'}
    return make_response(jsonify(res)), 201


@app.route('/api/login', methods=['POST'])
def signin_view():
    data = request.data
    userdata_dict = json.loads(data)
    username = userdata_dict.get('username')
    password = userdata_dict.get('password')
    print(userdata_dict)
    try:
        user = User.query.filter_by(username=username).first()

        validate_password = check_password_hash(user.password_hash, password)
        print(validate_password)
        if user and validate_password:
            auth_token = user.generate_authtoken(user.id)
            if auth_token:
                res = {
                    'message': 'Login Successful',
                    'Token': auth_token.decode()
                }
                return make_response(jsonify(res)), 200
        else:
            res = {
                'message': 'Invalid login credentials'
            }
            return make_response(jsonify(res)), 401
    except Exception:
        res = {
            'message': 'login failed, please try again'
        }
        return make_response(jsonify(res)), 500

