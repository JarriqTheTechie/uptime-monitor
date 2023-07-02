import logging

from masoniteorm.connections import ConnectionResolver

DATABASES = {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "database": "masonite.sqlite3",
        "log_queries": False,
    }
}

DB = ConnectionResolver().set_connection_details(DATABASES)

logger = logging.getLogger('masoniteorm.connection.queries')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)
