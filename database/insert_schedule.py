import pandas as pd
from database.db import get_cursor_connection

def insert_schedule(df):

    conn = get_cursor_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO schedule
    (game_date, away_team, home_team, result)
    VALUES (%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        result = VALUES(result);
    """

    cursor.executemany(
        sql,
        list(df.itertuples(index=False, name=None))
    )

    conn.commit()
    print(f"{cursor.rowcount}건 처리 완료")
    cursor.close()
    conn.close()


# 이 파일을 직접 실행할 때만 실행
if __name__ == "__main__":
    insert_schedule()
    
#단독 실행 가능
#Anaconda Prompt에서
#python insert_schedule.py 를 실행하면
#insert_schedule() 가 자동으로 실행됩니다.