import pandas as pd

df = pd.read_csv('./data/ranking_list.csv')
df['YYYYNN'] = df['year'].astype(str) + df['week'].astype(str).str.zfill(2)

df_top10 = df[df['ranking'].astype(int) <= 10].copy()
df_top10 = df_top10.sort_values(by=['artist', 'year', 'week'])

df_top10.to_csv('./data/no10_artists.csv', index=False)
