web: gunicorn --bind 0.0.0.0:$PORT app:app
worker: rq worker -u $REDISTOGO_URL places-info-tasks