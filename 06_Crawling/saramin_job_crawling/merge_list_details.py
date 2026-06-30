'''
리스트와 상세 정보 합치기
'''

import pandas as pd
import re

def clean_text(text):
    if not text:
        return ''
    clean = re.sub(r'[\x00-\x1f\x7f-\x9f​-‍﻿]', '', text)
    return clean

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()
    crolling_detail = pd.read_csv('./data/crolling_detail.csv')

    crolling_detail = crolling_detail[crolling_detail['content'].notnull() & (crolling_detail['content'] != '')]
    crolling_detail['content'] = crolling_detail['content'].map(lambda c: clean_text(c))

    for h in header:
        df = pd.read_csv(f'./data/02_{h}.csv')
        df['job_code'] = df['id'].str.split('-').str[1].astype(int)
        inner_join_df = pd.merge(df, crolling_detail, on='job_code', how='inner')
        inner_join_df.to_csv(f'./data/04_merged_details_{h}.csv', encoding='utf-8-sig')

main()
