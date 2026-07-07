import os
import pymysql

db_config = {
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "charset": "utf8mb4"
}


# Pandas 전용
def get_db_connection():
    return pymysql.connect(**db_config)


# Cursor 전용
def get_cursor_connection():
    return pymysql.connect(
        **db_config,
        cursorclass=pymysql.cursors.DictCursor
    )