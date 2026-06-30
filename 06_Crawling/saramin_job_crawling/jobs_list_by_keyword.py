'''
키워드별 채용공고 비율 차트
'''

import matplotlib.pyplot as plt
import koreanize_matplotlib

import pandas as pd

KEYWORDS = ['AI', '빅데이터', 'Python', 'LLM']

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    for k in KEYWORDS:
        s_labels = []
        s_radio = []
        for h in header:
            df = pd.read_csv(f'./data/{h}_{k.lower()}.csv', index_col=0)
            s_labels.append(h)
            s_radio.append(len(df))

        fig, ax = plt.subplots(figsize=(12, 8))
        title = f'[{k}] 키워드별 채용 공고 비율'
        ax.set_title(title)
        ax.pie(s_radio, labels=s_labels, autopct='%.1f%%', startangle=90)
        plt.tight_layout()
        fig.savefig(f'./data/output/chart/키워드별 채용공고 수 비교/{title}.png')

main()
