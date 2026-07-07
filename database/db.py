import pymysql

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "daeju_new",
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