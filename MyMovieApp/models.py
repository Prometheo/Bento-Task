from . import db
from flask import current_app as app, jsonify, request, make_response
from functools import wraps
import datetime
import jwt

class User(db.Model):
    """
    UserModel class
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(130))
    email = db.Column(db.String(80), unique=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    movies_list = db.relationship("Movies", secondary='personal_rating')

    def __repr__(self):
        return self.username
    
    #Generate Token for Authentication
    def generate_authtoken(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    #decode the provided token
    @staticmethod
    def decode_authtoken(authtoken):
        try:
            payload = jwt.decode(authtoken, app.config.get('SECRET_KEY'))
        except jwt.ExpiredSignatureError:
            return 'Token expired, log in again to create a new one'
        except jwt.InvalidTokenError:
            return 'Invalid token, log in again to create a new one'

        return payload['sub']
        

class Movies(db.Model):
    """ Moviesmodel class for storing movies """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(130), unique=True)
    rated_18 = db.Column(db.Boolean)
    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    release_date = db.Column(db.String(50))
    vote_average = db.Column(db.Float)

    def __repr__(self):
        return self.title
    
    @property
    def serializer(self):
        return {
            'id': self.id,
            'title': self.title,
            'rated_18': self.rated_18,
            'overview': self.overview,
            'popularity': self.popularity,
            'release_date': self.release_date,
            'vote_average': self.vote_average
        }

        
class PersonalRating(db.Model):
    __tablename__ = 'personal_rating'

    user_id =db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id',  ondelete="CASCADE"), primary_key=True)
    my_rating = db.Column(db.Float, server_default='0.0')
    my_comment = db.Column(db.String(300))
    added_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    movie = db.relationship(Movies)

    def __repr__(self):
        return "User_rating"
    


def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1]
        except:
            return jsonify({'message':'Token missen'})
        try:
            user_id = User.decode_authtoken(token)
            if isinstance(user_id, str):
                return make_response(jsonify({'message':user_id})), 404
            current_user = User.query.filter_by(id=user_id).first()
        except Exception as e:
            return jsonify(e)
        return f(current_user, *args, **kwargs)
    return wrap

