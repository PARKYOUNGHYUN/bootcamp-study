import pandas as pd
from utils.apple_api import get_earliest_release_date, artist_mapping

df = pd.read_csv('./data/no10_artists.csv')

idx = df.groupby('artist')['YYYYNN'].idxmin()
unique_df = df.loc[idx, ['artist', 'album', 'YYYYNN']].copy()
unique_df = unique_df.sort_values(by=['YYYYNN'])

for index, row in unique_df.iterrows():
    artist_name = row['artist']
    album_name = row['album']

    if ',' in artist_name:
        continue

    release_date = get_earliest_release_date(artist_name, album_name)
    if not release_date:
        retry_name = artist_mapping.get(artist_name)
        if retry_name:
            release_date = get_earliest_release_date(retry_name, album_name)
    if not release_date:
        print(f'{artist_name} not found')
        continue

    unique_df.loc[index, 'release_date'] = release_date

unique_df = unique_df.dropna(subset=['release_date'])
unique_df.to_csv('./data/no10_artists_release_date.csv')
