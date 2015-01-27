import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:postgres@localhost/search_rex'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'
    CELERY_BROKER_URL =\
        'sqla+postgresql://postgres:postgres@localhost/search_rex'


class HerokuConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']\
        if 'DATABASE_URL' in os.environ else\
        'postgresql://postgres:postgres@localhost/search_rex'
    CELERY_BROKER_URL = 'sqla+' + os.environ['DATABASE_URL']\
        if 'DATABASE_URL' in os.environ else\
        'sqla+postgresql://postgres:postgres@localhost/search_rex'
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
