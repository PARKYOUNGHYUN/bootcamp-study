import pandas as pd
from utils.apple_api import get_artist_albums, artist_mapping

df = pd.read_csv('./data/ranking_list.csv')
df['YYYYNN'] = df['year'].astype(str) + df['week'].astype(str).str.zfill(2)

idx = df.groupby('artist')['YYYYNN'].idxmin()
unique_df = df.loc[idx, ['artist', 'album', 'YYYYNN']].sort_values(by=['YYYYNN'])

album_list = set()
for index, row in unique_df.iterrows():
    artist_name = row['artist']
    album_name = row['album']

    albums = get_artist_albums(artist_name, album_name)
    if not albums:
        retry_name = artist_mapping.get(artist_name)
        if retry_name:
            retry_albums = get_artist_albums(retry_name, album_name)
            albums = [(artist_name, alb, date) for _, alb, date in retry_albums]
    if not albums:
        print(f'{artist_name} not found')
        continue
    if len(albums) <= 1:
        continue

    album_list.update(albums)

result_df = pd.DataFrame(list(album_list), columns=['artist', 'album', 'release_date'])
result_df = result_df.sort_values(by=['artist', 'release_date'])
result_df.to_csv('./data/albums_by_artist.csv', index=False)
