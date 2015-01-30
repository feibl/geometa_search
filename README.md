search-rex
==========

# Description
This application is a front-end to the geocat CSW server. It allows searching for geodata on the geocat.ch website. Moreover, it is an example project for the [search-rex](https://github.com/feibl/search-rex) recommender system that was implemented for the HSR-Geodatenkompass. This system learns users' interests by recording their individual search queries and search result selections in the application. By using this knowledge it is able to recommend search results to the users.

# Application Setup 
In order to setup the application the following tools are required:
* Python 2.7 environment
* A database such as PostgreSQL
* virtualenv
* virtualenvwrapper

After having installed the above listed tools, the following steps are to be performed in order to setup a running instance of the application:

#### 1. Clone the project:
```
$ git clone git@github.com:feibl/geometa_search.git
$ cd search_rex
```
#### 2. Create and initialize virtualenv for the project:
```
$ mkvirtualenv search_rex
$ pip install -r requirements.txt
```
#### 3. Set the configuration values for within the config.py file:
```python
class Config(object):
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:password@localhost/search_rex'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'
    CELERY_BROKER_URL =\
        'sqla+postgresql://postgres:password@localhost/search_rex'
    SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    SERVER_NAME = 'localhost:5000'
```
#### 4. Upgrade search-rex' database:
```
$ cdvirtualenv
$ cd src/search-recommender-origin
$ python manage.py db upgrade
```
#### 5. In a console, run the recommender application application:
```
$ cd search_rex
$ python run.py
```
#### 6. In another console, run the Celery application:
```
$ celery -A search_rex.tasks worker --loglevel=info --beat
```
#### 7. Open [http://localhost:5000](http://localhost:5000)

In the list entry 3, it can be seen that the API requires the specification of three configuration values. These configuration values are the following:
* `SQLALCHEMY_DATABASE_URI`: This configuration value tells the SQLAlchemy framework at which location the database can be found. It is specified in the form of a URI.
* `API_KEY`: This key is used to authenticate the caller who is calling one of the API's functions. It must be provided with every call directed to the API. Only if the key is correct, the function that is called is executed.
* `CELERY_BROKER_URL`: This configuration is needed in order to include the Celery task queue. Implementing this, Celery requires a solution to send and receive messages. This is achieved by using a message broker, a separate service where the messages are stored and consumed by the Celery workers. Examples of possible brokers are RabbitMQ, Redis or SQLAlchemy.
* `SERVER_NAME`: The url and the port at which the server is internally accessable
* `SECRET_KEY`: The secret key that is used by the application
