from geometa_search.factory import create_app as create_frontend
from search_rex.factory import create_app as create_backend
from search_rex.recommendations import create_recommender_system
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


backend = create_backend('recsys_config.HerokuConfig')
create_recommender_system(backend)
frontend = create_frontend('config.DevelopmentConfig')
app = DispatcherMiddleware(
    frontend, {
        '/recommender': backend
    }
)
print('app created')

if __name__ == '__main__':
    run_simple(
        'localhost', 5000, app, use_reloader=True,
        use_debugger=True, threaded=True)
