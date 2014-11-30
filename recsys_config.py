import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:postgres@localhost/search_rex'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI =\
        'sqlite:////tmp/search_rex.db'
