from os import environ, path


basedir = path.abspath(path.dirname(__file__))


class Config:

    FLASK_ENV = environ.get('FLASK_ENV')
    DEBUG = True
    SECRET_KEY = environ.get('SECRET_KEY')


    #Database configs

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL', '')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
