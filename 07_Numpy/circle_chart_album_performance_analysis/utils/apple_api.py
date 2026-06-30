import requests

artist_mapping = {
    '걸스데이 (Girl`s Day)': '걸스데이',
    '황광희 X 개코': '황광희',
    "BE`O (비오)": "BE'O"
}

def _get_artist_id(artist_name, album_name):
    try:
        res = requests.get(f"https://itunes.apple.com/search?term={artist_name}&entity=musicArtist").json()
        if res['resultCount'] > 0:
            return res['results'][0]['artistId']
    except Exception:
        pass

    try:
        res = requests.get(f"https://itunes.apple.com/search?term={album_name}&entity=album").json()
        if res['resultCount'] > 0:
            return res['results'][0]['artistId']
    except Exception:
        pass

    return None

def _fetch_album_results(artist_id):
    try:
        res = requests.get(f"https://itunes.apple.com/lookup?id={artist_id}&entity=album").json()
        return res['results']
    except Exception:
        return []

def get_artist_albums(artist_name, album_name):
    """trackCount >= 4이고 Single이 아닌 앨범 목록을 반환한다.
    Returns list of (artist_name, collection_name, release_date) tuples.
    """
    artist_id = _get_artist_id(artist_name, album_name)
    if not artist_id:
        return []

    albums = []
    for item in _fetch_album_results(artist_id):
        if item.get('trackCount', 0) < 4:
            continue
        collection_name = item.get('collectionName', '')
        if '- Single' in collection_name:
            continue
        albums.append((artist_name, collection_name, item['releaseDate']))
    return albums

def get_earliest_release_date(artist_name, album_name):
    """iTunes에서 아티스트의 가장 빠른 releaseDate를 반환한다. 없으면 None."""
    artist_id = _get_artist_id(artist_name, album_name)
    if not artist_id:
        return None

    results = _fetch_album_results(artist_id)
    dates = [item['releaseDate'] for item in results if 'releaseDate' in item]
    return min(dates) if dates else None
