#import pymysql 
#import numpy as np
#import pandas as pd
from db import get_cursor_connection

# 🗄️ MySQL용 테이블 초기화 함수
def init_db():
    conn = get_cursor_connection()
    cursor = conn.cursor()
    
    # MySQL 문법에 맞게 AUTO_INCREMENT 및 데이터 타입 조정
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()
print("users 테이블 생성 완료")

# schedule 테이블 생성
conn = get_cursor_connection()
cursor = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_date DATE NOT NULL,
    away_team VARCHAR(20) NOT NULL,
    home_team VARCHAR(20) NOT NULL,
    result VARCHAR(20) NOT NULL
)
"""

cursor.execute(sql)

conn.commit()

cursor.close()
conn.close()

print("schedule 테이블 생성 완료")