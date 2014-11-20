from geometa_search import create_app

if __name__ == '__main__':
    app = create_app('config.DevelopmentConfig')
    app.run(debug=True)
