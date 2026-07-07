from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import logging


# ===============================
# 개발용 / 자동실행용 설정
# ===============================
HEADLESS = False      # 개발할 때 False
# HEADLESS = True     # 작업스케줄러에서는 True


# ===============================
# 로그 설정
# ===============================
logging.basicConfig(
    filename="crawl_schedule.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


def crawl_schedule():

    logging.info("========== 크롤링 시작 ==========")

    cal_data = []

    option = Options()

    if HEADLESS:
        # Chrome 창을 화면에 띄우지 말고 백그라운드에서 실행하라.
        option.add_argument("--headless=new")
    else:
        # 프로그램이 끝나도 Chrome 창을 바로 닫지 말라
        # detach : 분리하다
        option.add_experimental_option("detach", True)
    # GPU(그래픽카드) 가속을 사용하지 않습니다.
    option.add_argument("--disable-gpu")
    # Chrome의 보안 샌드박스를 사용하지 않습니다.
    option.add_argument("--no-sandbox")
    # 공유 메모리(/dev/shm)를 사용하지 않습니다.
    option.add_argument("--disable-dev-shm-usage")
    # 나는 Windows 10의 일반 브라우저입니다. -> 일반 사용자의 Chrome처럼 접속
    option.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
     )

    driver = None

    try:

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=option
        )

        logging.info("크롬 실행")

        driver.get("https://www.koreabaseball.com/Schedule/Schedule.aspx")

        wait = WebDriverWait(driver, 10)

        wait.until(
            EC.presence_of_element_located((By.ID, "ddlYear"))
        )

        logging.info("사이트 접속 완료")

        select = Select(driver.find_element(By.ID, "ddlYear"))
        select.select_by_value("2026")

        wait.until(
            EC.presence_of_element_located((By.ID, "ddlMonth"))
        )

        months = ["07", "08", "09"]

        for num in months:

            logging.info(f"{num}월 크롤링 시작")

            select = Select(driver.find_element(By.ID, "ddlMonth"))
            select.select_by_value(num)

            wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            current_day = ""

            tr_list = driver.find_elements(By.TAG_NAME, "tr")

            for tr in tr_list:

                days = tr.find_elements(By.CLASS_NAME, "day")

                if days:
                    current_day = days[0].text

                players = tr.find_elements(By.CLASS_NAME, "play")

                for player in players:

                    spans = player.find_elements(By.TAG_NAME, "span")

                    if len(spans) == 5:

                        team_a = spans[0].text
                        #vs = spans[2].text
                        team_b = spans[4].text

                        score1 = int(spans[1].text)
                        score2 = int(spans[3].text)

                        if score1 > score2:
                            result = f"{team_a}승"

                        elif score1 == score2:
                            result = "무승부"

                        else:
                            result = f"{team_b}승"
                        #print(f'{current_day} {team_a} {team_b} {label}')
                        cal_data.append([
                            current_day,
                            team_a,
                            team_b,
                            result
                        ])

                    elif len(spans) >= 3:

                        team_a = spans[0].text
                        #vs = spans[1].text
                        team_b = spans[2].text
                        #print(f'{current_day} {team_c} {team_d} 예정')
                        cal_data.append([
                            current_day,
                            team_a,
                            team_b,
                            "예정"
                        ])

            logging.info(f"{num}월 완료")

        df = pd.DataFrame(
            cal_data,
            columns=[
                "game_date",
                "away_team",
                "home_team",
                "result"
            ]
        )
        # 07.01(수) --> 2026-07-01
        # regex=False : 문자열을 정규표현식(Regex)으로 해석하지 말고, 있는 그대로 문자로 처리하라
        df["game_date"] = (
            "2026-"
            + df["game_date"]
            .str.split("(")
            .str[0]
            .str.replace(".", "-", regex=False)
        )

        logging.info(f"총 {len(df)} 경기 수집")

        print(f"총 {len(df)} 경기 수집 완료")
        #df.to_csv("schedule.csv", index=False, encoding="utf-8-sig")
        return df

    except Exception as e:

        logging.exception(e)
        print(e)

        return pd.DataFrame()

    finally:

        if driver is not None:
            driver.quit()

        logging.info("브라우저 종료")
        logging.info("========== 크롤링 종료 ==========\n")

# 이 파일을 직접 실행할 때만 실행
if __name__ == "__main__":

    df = crawl_schedule()

    print(df.head())