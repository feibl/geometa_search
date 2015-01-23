from flask import Flask


def create_app(config_path):
    app = Flask(__name__)
    app.config.from_object(config_path)

    from .views import meta_search as search_module
    app.register_blueprint(search_module)

    return app
