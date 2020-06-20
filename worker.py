from rq import Connection, Worker

from places_info import app
from places_info.places_info_utils import queue, redis_connection

if __name__ == "__main__":
    with app.server.app_context():
        with Connection(redis_connection):
            w = Worker([queue])
            w.work()
