from geometa_search import create_app as create_frontend
from search_rex.factory import create_app as create_backend
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


backend = create_backend('recsys_config.DevelopmentConfig')
frontend = create_frontend('config.DevelopmentConfig')
app = DispatcherMiddleware(
    frontend, {
        '/recommender': backend
    }
)

if __name__ == '__main__':
    run_simple(
        'localhost', 5000, app, use_reloader=True,
        use_debugger=True, threaded=True)
