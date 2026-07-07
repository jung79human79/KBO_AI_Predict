import os
import pymysql

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
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