import os

DB_CONFIG = {
    "dbname": os.getenv("DB_CONFIG_DBNAME"),
    "user": os.getenv("DB_CONFIG_USER"),
    "password": os.getenv("DB_CONFIG_PASSWORD"),
    "host": os.getenv("DB_CONFIG_HOST"),
    "port": int(os.getenv("DB_CONFIG_PORT")),
}
