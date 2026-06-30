'''
신입 vs 경력 vs 경력무관 비율 차트
'''

import matplotlib.pyplot as plt
import koreanize_matplotlib

import pandas as pd
import numpy as np

from utils import classify_refined

labels = ['경력', '경력무관', '신입']
palette = ['#5eabee', '#de93f8', '#fddb8b']

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    for h in header:
        values = []

        df = pd.read_csv(f'./data/02_{h}.csv')
        df = df.dropna(subset=['career'])

        df['clean_career'] = df['career'].apply(classify_refined)
        df = df.dropna(subset=['clean_career'])

        for k in labels:
            target_df = df[df['clean_career'] == k]
            values.append(len(target_df))

        fig, ax = plt.subplots(figsize=(15, 10))
        title = f'[{h}] 신입 vs 경력vs 경력무관 비율'
        ax.set_title(title, fontsize=20)
        plt.tight_layout()

        ax.pie(values, labels=labels, autopct='%.1f%%', startangle=90, colors=palette)
        fig.savefig(f'./data/output/chart/신입 vs 경력vs 경력무관 비율/{title}.png')

        plt.close(fig)

main()
