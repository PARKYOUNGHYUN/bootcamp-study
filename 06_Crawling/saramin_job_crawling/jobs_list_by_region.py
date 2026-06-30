'''
지역별 채용공고 비교 차트
'''

import matplotlib.pyplot as plt
import koreanize_matplotlib

import pandas as pd

KEYWORDS = ['AI', '빅데이터', 'Python', 'LLM']

def main():
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    sorted_regions = [
        '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
        '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
    ]
    palette = {
        '서울': '#ff9896', '경기': "#e6d169", '인천': "#5ea02c", '부산': '#d62728',
        '대구': '#9467bd', '대전': '#8c564b', '광주': '#1f77b4', '경남': '#bcbd22',
        '경북': '#7f7f7f', '충남': '#17becf', '충북': '#aec7e8', '세종': '#ffbb78', '제주': '#ff7f0e', '울산': '#e377c2',
        '강원': '#c5b0d5', '전북': '#c49c94', '전남': '#dbdb8d', '기타(전국, 해외 등)': '#c7c7c7'
    }

    for h in header:
        fig, axes = plt.subplots(2, 2, figsize=(25, 10))

        title = f'{h}별 비율'
        fig.suptitle(title, fontsize=20)
        fig.tight_layout()

        x = 0
        y = 0
        for i, k in enumerate(KEYWORDS):
            if i == 1:
                y = 1
            elif i == 2:
                x = 1
                y = 0
            elif i == 3:
                y = 1

            df = pd.read_csv(f'./data/{h}_{k.lower()}.csv', index_col=0)
            df = df.dropna(subset=['region'])
            df['splited_region'] = df['region'].str.split(' ').str[0].str[:2]
            df['splited_region'] = df['splited_region'].apply(lambda x: x if x in sorted_regions else '기타(전국, 해외 등)')

            indexes = df['splited_region'].value_counts().index.tolist()
            values = df['splited_region'].value_counts().values.tolist()

            colors = [palette[index] for index in indexes]

            xtick = range(1, len(indexes) + 1)
            axes[x, y].set_title(k)
            axes[x, y].bar(xtick, values, color=colors)
            axes[x, y].set_xticks(xtick, labels=indexes, rotation=45)

        plt.tight_layout()
        plt.savefig(f'./data/output/chart/지역별 채용공고 비교/{title}.png')

main()
