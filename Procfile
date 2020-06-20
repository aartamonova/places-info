web: bin/start-nginx gunicorn -c config/gunicorn.conf.py --bind 0.0.0.0:$PORT 'app:create_app()'
worker: python worker.py