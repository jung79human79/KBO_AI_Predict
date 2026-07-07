from crawler.crawl_schedule import crawl_schedule
from database.insert_schedule import insert_schedule

print("업데이트 시작")

df = crawl_schedule()     # DataFrame 반환

if not df.empty:
    insert_schedule(df)
    print("DB 저장 완료")
else:
    print("수집된 데이터가 없습니다.")