from geometa_search import create_app as create_frontend
from search_rex.factory import create_app as create_backend
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


if __name__ == '__main__':
    frontend = create_frontend('config.DevelopmentConfig')
    backend = create_backend('recsys_config.DevelopmentConfig')
    app = DispatcherMiddleware(
        frontend, {
            '/recommender': backend
        }
    )
    run_simple('localhost', 5000, app, use_reloader=True, threaded=True)
