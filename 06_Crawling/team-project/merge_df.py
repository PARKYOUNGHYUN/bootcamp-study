'''
df 합치기
'''

import pandas as pd

KEYWORDS = ['ai', '빅데이터', 'python', 'llm']

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    df_all_list = []
    for h in header:
        df_list = []
        for k in KEYWORDS:
            df = pd.read_csv(f'./data/{h}_{k}.csv', index_col=0)
            df_list.append(df)
        result_row = pd.concat(df_list, ignore_index=True)
        result_row = result_row.drop_duplicates(subset=['id'], keep='first')
        print(result_row.head())
        result_row.to_csv(f'./data/02_{h}.csv', index=False)

        df_all_list.append(result_row)

    result_row = pd.concat(df_all_list, ignore_index=True)
    print(len(result_row))
    result_row = result_row.drop_duplicates(subset=['id'], keep='first')
    print(len(result_row))
    result_row.to_csv(f'./data/01_all.csv', index=False)

main()
