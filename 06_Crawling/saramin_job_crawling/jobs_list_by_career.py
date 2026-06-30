'''
경력에 따른 고용형태 차트
'''

import matplotlib.pyplot as plt
import koreanize_matplotlib

import pandas as pd
import numpy as np

from utils import classify_refined

labels = ['경력', '경력무관', '신입']
palette = ["#5eabee", "#de93f8", "#fddb8b"]

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    for h in header:
        values_fulltime = []
        values_temp = []

        df = pd.read_csv(f'./data/02_{h}.csv')
        df = df.dropna(subset=['career'])

        df['clean_career'] = df['career'].apply(classify_refined)
        df = df.dropna(subset=['clean_career'])

        for k in labels:
            target_df = df[df['clean_career'] == k]

            fulltime_count = len(target_df[target_df['career'].str.contains('정규직')])
            temp_count = len(target_df[target_df['career'].str.contains('계약직')])

            values_fulltime.append(fulltime_count)
            values_temp.append(temp_count)

        fig, ax = plt.subplots(figsize=(15, 10))
        title = f'[{h}] 경력에 따른 고용형태'
        ax.set_title(title, fontsize=20)

        xtick = np.arange(len(labels))
        width = 0.4

        ax.bar(xtick - width / 2, values_fulltime, width, label='정규직', color=palette[0])
        ax.bar(xtick + width / 2, values_temp, width, label='계약직', color=palette[1])
        ax.set_xticks(xtick, labels=labels)
        ax.set_xlabel('경력구분')
        ax.set_ylabel('채용공고 수')
        ax.legend(fontsize=15)
        plt.tight_layout()
        fig.savefig(f'./data/output/chart/경력에 따른 고용형태/{title}.png')

        plt.close(fig)

main()
