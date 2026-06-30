import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import koreanize_matplotlib

one_df = pd.read_csv('./data/success_df.csv')
second_df = pd.read_csv('./data/success_sophomore.csv')
ranking_list_df = pd.read_csv('./data/ranking_list.csv')

concat_df = pd.concat([one_df, second_df], axis=0)
result = pd.merge(ranking_list_df, concat_df[['artist', 'album']], on=['artist', 'album'], how='inner')

unique_df = result.groupby(['artist', 'album']).head(1)
unique_df = unique_df.groupby(['artist']).filter(lambda x: len(x) == 2)
unique_df = unique_df.sort_values(by=['artist', 'year', 'week'])

# 첫 차트인 순위 박스플롯
first_rows = unique_df.groupby(['artist']).nth(0)
second_rows = unique_df.groupby(['artist']).nth(1)

plt.figure(figsize=(8, 6))
plt.boxplot([list(first_rows['ranking']), list(second_rows['ranking'])], orientation='vertical')
plt.xticks([1, 2], ['1번째 앨범', '2번째 앨범'])
plt.title('첫 차트인 순위')
plt.ylabel('순위')
plt.show()

# 앨범별 최고 순위 박스플롯
result2 = pd.merge(ranking_list_df, unique_df[['artist', 'album']], on=['artist', 'album'], how='inner')
result2 = result2.sort_values(by=['artist', 'year', 'week'])
min_rank_df = result2.groupby(['artist', 'album'])['ranking'].agg(['min'])

first_rows_min = min_rank_df.groupby(['artist']).nth(0)
second_rows_min = min_rank_df.groupby(['artist']).nth(1)

plt.figure(figsize=(8, 6))
plt.boxplot([list(first_rows_min['min']), list(second_rows_min['min'])], orientation='vertical')
plt.xticks([1, 2], ['1번째 앨범', '2번째 앨범'])
plt.title('앨범별 최고 순위')
plt.ylabel('순위')
plt.show()

# 차트 유지 평균 주수 바 차트
result3 = pd.merge(ranking_list_df, unique_df[['artist', 'album']], on=['artist', 'album'], how='inner')
result3 = result3.sort_values(by=['artist', 'year', 'week'])
longevity = result3.groupby(['artist', 'album']).size()

first_mean = longevity.groupby(['artist']).nth(0).values.mean()
second_mean = longevity.groupby(['artist']).nth(1).values.mean()

plt.figure(figsize=(8, 6))
plt.bar([0, 1], [first_mean, second_mean])
plt.xticks([0, 1], labels=['1번째 앨범', '2번째 앨범'])
plt.ylabel('n주')
plt.title('차트에 머문 평균 주수')
plt.show()
