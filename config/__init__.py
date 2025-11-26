from dotenv import load_dotenv, find_dotenv
import os

path_dotenv = find_dotenv()
assert path_dotenv, "Arquivo .env não encontrado"
load_dotenv(path_dotenv)

config = {
    "api_id": os.getenv("APP_IP"),
    "api_hash": os.getenv("API_HASH"),
    "session": os.getenv("SESSION_NAME"),
    "phone": os.getenv("PHONE_NUMBER"),
    "phpass": os.getenv("TEL_PASSWORD"),
}

db_config = {
    "dbname": os.getenv("DB_CONFIG_DBNAME"),
    "user": os.getenv("DB_CONFIG_USER"),
    "password": os.getenv("DB_CONFIG_PASSWORD"),
    "host": os.getenv("DB_CONFIG_HOST"),
    "port": os.getenv("DB_CONFIG_PORT")
}

db_url = {
    "urlpg": os.getenv("DATABASE_URL")
}

app_shortname=os.getenv("SHORTNAME")
app_title=os.getenv("APP_TITLE")