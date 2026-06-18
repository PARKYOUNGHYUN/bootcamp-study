'''
사람인 채용공고 상세 페이지 크롤링

- 작성자: 박영현
- 작성일자: 2026.02.21
'''

from selenium import webdriver
from selenium.webdriver.common.by import By

import pandas as pd
import time
import random
import csv
from datetime import datetime

URL = 'https://www.saramin.co.kr/zf_user/jobs/relay/view-detail'

def create_chrome_options(process_id):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument(f"user-agent={user_agents[process_id % 3]}")

    return options

def main():

    process_id = 0

    all_df = pd.read_csv('./data/01_all.csv')

    driver = webdriver.Chrome(options=create_chrome_options(process_id))
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)

    details_df = pd.read_csv('./data/crolling_detail.csv', encoding='utf-8-sig')
    details_df = details_df[~details_df['content'].str.contains('사이트에 연결할 수 없음', na=False)]

    all_codes = all_df['id'].str.split('-').str[1].astype(str)
    crawled_codes = details_df['job_code'].astype(str)

    not_crawled_ids = all_df[~all_codes.isin(crawled_codes)]['id'].str.split('-').str[1].unique()

    with open('./data/crolling_detail.csv', 'a', newline='', encoding='utf-8-sig') as f:
        with open('./data/error_log.txt', 'a', encoding='utf-8-sig') as log:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(['job_code', 'content'])

            size = len(not_crawled_ids)
            crawl_count = 0
            for code in not_crawled_ids:
                path = f'?rec_idx={code}&rec_seq=0&t_category=non-logged_relay_view&t_content=view_detail&t_ref=&t_ref_content='
                url = URL + path
                print(url)

                try:
                    driver.get(url)
                    time.sleep(random.uniform(2.5, 4.5))

                    content = driver.find_element(By.TAG_NAME, "body").get_attribute('innerText')
                    writer.writerow([code, content.replace('\n', ' ').strip()])

                    crawl_count += 1

                    if crawl_count % 10 == 0:
                        f.flush()
                        print(f"[{crawl_count}/{size}] 수집 완료 (CODE: {code})")

                    if crawl_count % 100 == 0:
                        print("--- 1분간 휴식 (차단 방지) ---")
                        time.sleep(60)

                    if crawl_count % 500 == 0:
                        driver.quit()
                        process_id += 1
                        driver = webdriver.Chrome(options=create_chrome_options(process_id))
                        driver.implicitly_wait(5)

                except Exception as e:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    error_msg = f"[{now}] ID: {code} | 에러: {str(e)}\n"
                    log.write(error_msg)
                    log.flush()
                    print(f"{code} 실패")
                    continue

    driver.quit()
    print('end')

main()
