import os
from dotenv import load_dotenv, find_dotenv
path_dotenv = find_dotenv()
load_dotenv(path_dotenv, override=True)


DB_CONFIG = {
    "dbname": os.getenv("DB_CONFIG_DBNAME"),
    "user": os.getenv("DB_CONFIG_USER"),
    "password": os.getenv("DB_CONFIG_PASSWORD"),
    "host": os.getenv("DB_CONFIG_HOST"),
    "port": os.getenv("DB_CONFIG_PORT"),
}
