from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://circlechart.kr/page_chart/onoff.circle?serviceGbn=ALL&termGbn=week'

def main():
    html = urlopen(URL)
    bs = BeautifulSoup(html, 'html.parser')

    options = bs.select('.float-right select > option')
    df_list = []
    for option in options:
        value = option.attrs['value']
        if not value:
            continue

        period = option.text[:21].split('~')
        start_date = period[0]
        end_date = period[1]

        df_list.append([value, start_date, end_date])

    df = pd.DataFrame(df_list, columns=['YYYYNN', 'start_date', 'end_date'])
    df = df.set_index('YYYYNN')
    df.to_csv('./data/period.csv')

main()
