import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "172.30.1.12"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "team1"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "team1_01"),
    "charset": "utf8",
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def get_engine():
    from sqlalchemy import create_engine
    c = DB_CONFIG
    return create_engine(
        f"mysql+pymysql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"
    )
