'''
사람인 채용공고 리스트 크롤링

- 작성자: 박영현
- 작성일자: 2026.02.20
'''

from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup

import pandas as pd

KEYWORDS = ['ai', '빅데이터', 'python', 'llm']

URL = 'https://www.saramin.co.kr/zf_user/jobs/list/industry?'

def create_url(codes, page, keyword):
    JOIN_STR = '%2C'

    query_strings = []
    query_strings.append(f'ind_cd={JOIN_STR.join(codes)}')
    query_strings.append(f'&page={page}')
    query_strings.append(f'&job_type=1%2C2')
    query_strings.append(f'&searchType=search&searchword={quote(keyword)}&search_optional_item=y&search_done=y&panel_count=y&preview=y&isAjaxRequest=0&page_count=50&sort=RL&type=industry&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=2')

    return URL + ''.join(query_strings)

def main():

    codes_df = pd.read_csv('./data/00_code.csv')

    codes_dic = {}
    for c in list(codes_df.columns):
        codes_dic[c] = codes_df[c].dropna().astype(int).astype(str).to_list()

    for key, codes in codes_dic.items():
        print(key)

        for k in KEYWORDS:
            df_list = []
            page = 1
            while True:
                url = create_url(codes, page, k)
                print(url)
                html = urlopen(url)
                bs = BeautifulSoup(html, 'html.parser')

                announcement_list = bs.select('.list_body .list_item')
                if not announcement_list:
                    print('페이지 확인 안됨')
                    break
                for announcement in announcement_list:
                    data = []

                    id = announcement.attrs['id']
                    company_a = announcement.select_one('.company_nm a')
                    if company_a:
                        company_name = str(company_a.text).strip()
                        company_link = company_a.attrs['href']
                    else:
                        company_name = announcement.select_one('.company_nm span').text
                        company_link = ''

                    job_a = announcement.select_one('.job_tit a')
                    job_name = job_a.text
                    job_link = job_a.attrs['href']

                    data.append(id)
                    data.append(job_name)
                    data.append(job_link)

                    recruit_info = announcement.select_one('.recruit_info')
                    work_place = recruit_info.select_one('.work_place')
                    career = recruit_info.select_one('.career')
                    education = recruit_info.select_one('.education')

                    data.append(work_place.text if work_place else '')
                    data.append(career.text if career else '')
                    data.append(education.text if education else '')

                    meta_list = announcement.select('.job_meta .job_sector span')
                    comma_strings = ','.join(map(lambda meta: meta.text, meta_list))
                    data.append(comma_strings)

                    data.append(company_name)
                    data.append(company_link)

                    df_list.append(data)

                page += 1

            df = pd.DataFrame(df_list, columns=['id', 'job_name', 'job_link', 'region', 'career', 'education', 'metadata', 'company_name', 'company_link'])
            df.to_csv(f'./data/{key}_{k}.csv', encoding='utf-8-sig')

main()
