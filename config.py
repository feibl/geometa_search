import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'
    SERVER_NAME = 'localhost:5000'


class HerokuConfig(Config):
    DEBUG = True
    TESTING = True
    SERVER_NAME = 'lit-retreat-7902.herokuapp.com'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
