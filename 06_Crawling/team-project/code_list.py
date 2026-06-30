'''
사람인 산업 코드 가져오기

- 작성자: 박영현
- 작성일자: 2026.02.21
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup

import pandas as pd


def parser_code_list():
    url = 'https://oapi.saramin.co.kr/guide/code-table3'

    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')

    return bs

def get_m_categories_dic(bs):

    # 상위 산업/업종 코드
    bot_tr_list = bs.select('#botCodelist tbody tr')

    l_category_dic = {}
    for tr in bot_tr_list:
        td_list = tr.select('td')
        l_category_dic[td_list[0].text] = td_list[1].text

    # 산업/업종 코드표
    las_tr_list = bs.select('#lasCodelist tbody tr')

    m_categories_dic = {}
    for k, v in l_category_dic.items():
        category = []
        for tr in las_tr_list:
            td_list = tr.select('td')
            num = int(td_list[0].text) // 100
            if num == int(k):
                category.append(td_list[0].text)
        m_categories_dic[v] = category

    return m_categories_dic

def main():
    bs = parser_code_list()
    m_categories_dic = get_m_categories_dic(bs)
    print(m_categories_dic)
    df = pd.DataFrame.from_dict(m_categories_dic, orient='index').transpose()
    df.to_csv('./data/00_code.csv', na_rep='', index=False)

main()
