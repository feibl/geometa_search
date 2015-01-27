web: gunicorn run_heroku:app --log-file=-
beat: celery beat --app=search_rex.tasks.celery --loglevel=info
