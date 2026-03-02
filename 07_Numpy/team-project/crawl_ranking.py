import requests
import pandas as pd
import numpy as np
import time
import datetime

def get_weekly_data(year, week):
    year = str(year)
    week = str(week).zfill(2)

    path = 'serviceGbn=ALL&termGbn=week&hitYear={year}&targetTime={week}&nationGbn=K&year_time='
    target_url_part = f"circlechart.kr/page_chart/onoff.circle?" + path

    payload = {
        'nationGbn': 'K',
        'serviceGbn': 'ALL',
        'termGbn': 'week',
        'hitYear': year,
        'targetTime': week,
        'yearTime': '3',
        'curUrl': target_url_part
    }

    url = "https://circlechart.kr/data/api/chart/onoff"
    headers = {
        'referer': f'https://' + target_url_part,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    res = requests.post(url, data=payload, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        print(f"에러 발생: {res.status_code}")
        print(res.text)

def to_dataframe(year, week, songs):
    rows = []
    for i in range(len(songs)):
        song = songs[str(i)]
        rows.append({
            'year': year,
            'week': week,
            'ranking': song['SERVICE_RANKING'],
            'score': song['ROW_CNT'],
            'album': song['ALBUM_NAME'],
            'artist': song['ARTIST_NAME'],
        })
    return pd.DataFrame(rows)

def main():
    year = 2010
    week = 1
    while True:
        try:
            data = get_weekly_data(year, week)

            time.sleep(np.random.uniform(1.0, 2.5))

            if data['ResultStatus'] == 'Error':
                print(f'[success] {year}년 완료')
                year += 1
                week = 1
                continue

            df = to_dataframe(year, week, data['List'])
            df.to_csv('./data/ranking_list.csv', mode='a', header=False, index=False)

            week += 1
            if year == 2027:
                break

        except Exception as e:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[error({now})] {year}년 {week}주차 실패 | 에러: {str(e)}')
            continue

main()
