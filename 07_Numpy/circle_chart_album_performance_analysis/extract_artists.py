import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

albums_df = pd.read_csv('./data/albums_by_artist.csv')
period_df = pd.read_csv('./data/period.csv')
ranking_df = pd.read_csv('./data/ranking_list.csv')

ranking_df['YYYYNN'] = ranking_df['year'].astype(str) + ranking_df['week'].astype(str).str.zfill(2)

# 아티스트별 최초 차트 진입 주차(YYYYNN)와 해당 주의 시작일 확보
first_entry_idx = ranking_df.groupby('artist')['YYYYNN'].idxmin()
first_entry = ranking_df.loc[first_entry_idx, ['artist', 'YYYYNN']].reset_index(drop=True)
first_entry = first_entry.merge(period_df[['YYYYNN', 'start_date']], on='YYYYNN', how='left')
first_entry['start_date'] = pd.to_datetime(first_entry['start_date'], format='%Y.%m.%d')

# iTunes 앨범 목록과 최초 차트 진입일 결합
albums_df['release_date'] = pd.to_datetime(albums_df['release_date'], format='%Y-%m-%dT%H:%M:%SZ')
df = albums_df.merge(first_entry[['artist', 'YYYYNN', 'start_date']], on='artist', how='inner')
df['diff'] = (df['start_date'] - df['release_date']).dt.days

# 발매일 기준 10일 이내 차트 진입한 앨범 (1집 데뷔 조건)
in_chart_10_df = df[(df['diff'] >= 0) & (df['diff'] <= 10)].copy()
print(f"발매일 10일 이내로 10위권 차트인 데이터 개수: {len(in_chart_10_df)}건")
in_chart_10_df.to_csv('./data/success_df.csv')

in_charts_10_artists = in_chart_10_df['artist'].unique().tolist()

is_rising = 0
is_falling = 0
is_stable = 0
sophomore_rows = []

for artist in in_charts_10_artists:
    artist_chart_df = ranking_df[ranking_df['artist'] == artist]

    # 차트에 오른 앨범이 1개뿐이면 2집 비교 불가
    if len(artist_chart_df['album'].unique()) == 1:
        continue

    artist_chart_df = artist_chart_df.sort_values(by=['year', 'week'])
    first_entry_per_album = artist_chart_df.groupby(['artist', 'album']).head(1)

    if len(first_entry_per_album) < 2:
        continue

    first_album = first_entry_per_album.iloc[0]
    second_album = first_entry_per_album.iloc[1]

    sophomore_rows.append(second_album.to_dict())

    diff = first_album['ranking'] - second_album['ranking']
    if diff == 0:
        is_stable += 1
    elif diff < 0:
        is_rising += 1
    else:
        is_falling += 1

pd.DataFrame(sophomore_rows).to_csv('./data/success_sophomore.csv', index=False)

keys = ['하락', '상승', '변화없음']
values = [is_falling, is_rising, is_stable]

plt.figure(figsize=(8, 8))
plt.pie(values, labels=keys, autopct='%.1f%%', startangle=90)
title = '앨범 첫 차트인 순위 1집 대비 2집 변화'
plt.title(title, fontsize=20)
plt.tight_layout()
plt.savefig(f'./data/output/chart/{title}.png')
