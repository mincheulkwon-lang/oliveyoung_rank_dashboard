import time
import schedule

from datetime import datetime

from config import CRAWL_TIMES
from crawler import crawl_all_categories
from database import insert_log


def job():
    try:
        print(f"[자동 수집 시작] {datetime.now()}")

        inserted = crawl_all_categories()

        insert_log(
            "전체",
            "SUCCESS",
            f"자동 수집 완료: {inserted}건"
        )

        print(f"[자동 수집 완료] {inserted}건")

    except Exception as e:
        insert_log(
            "전체",
            "ERROR",
            f"자동 수집 실패: {e}"
        )

        print(f"[자동 수집 실패] {e}")


for crawl_time in CRAWL_TIMES:
    schedule.every().day.at(crawl_time).do(job)
    print(f"자동 수집 예약 완료: {crawl_time}")


print("자동 수집 대기 중입니다.")

while True:
    schedule.run_pending()
    time.sleep(30)