'''
워드클라우드 생성
'''

from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import koreanize_matplotlib

import pandas as pd
import re

SEARCH_INC_LIST = ['IT·웹·통신']
KEYWORDS = ['ai', '빅데이터', 'python', 'llm']

def main(extract_keyword=False):
    header = pd.read_csv('./data/00_code.csv', nrows=0).columns.tolist()

    for h in header:
        if h not in SEARCH_INC_LIST:
            continue

        if not extract_keyword:
            print(h)
            df = pd.read_csv(f'./data/02_{h}.csv')
            new_keywords_list = create_keywords(df)
            tags = create_tags(new_keywords_list, KEYWORDS)
            print(tags)
        else:
            for k in KEYWORDS:
                print(f'{h}_{k}')
                df = pd.read_csv(f'./data/{h}_{k}.csv', index_col=0)
                new_keywords_list = create_keywords(df)
                tags = create_tags(new_keywords_list, [k])
                print(tags)
                draw_image(f'{h}_{k}', tags)
        print()

def create_keywords(df):
    keywords = df['metadata'].values.tolist()

    new_keywords_list = list()
    for k in keywords:
        pattern = r'[^가-힣a-zA-Z0-9/+.#&\-]'
        concat_str_list = set(re.findall(pattern, k))

        if concat_str_list:
            escape_str = ''.join(concat_str_list)
            s = re.escape(escape_str)
            k = re.split(f'[{s}]', k)
            k = [word for word in k if word]
            new_keywords_list.extend(k)
        else:
            new_keywords_list.append(k)

    return new_keywords_list

def create_tags(new_keywords_list, stopwords):
    counts = Counter(word.upper() for word in new_keywords_list)
    tags = counts.most_common(len(new_keywords_list))
    tag_dict = dict(tags)
    for stopword in stopwords:
        stopword = stopword.upper()
        if stopword in tag_dict:
            tag_dict.pop(stopword)

    return tag_dict

def draw_image(title, tags):
    path = r'c:\Windows\Fonts\malgun.ttf'

    img_mask = np.array(Image.open('./data/image/cloud.png'))
    wc = WordCloud(font_path=path, width=400, height=400,
                   background_color="white", max_font_size=200,
                   colormap='inferno', mask=img_mask)
    cloud = wc.generate_from_frequencies(tags)
    cloud.to_file(f'./data/output/wordCloud/{title}.jpg')
    plt.figure(figsize=(10, 8))
    plt.axis('off')
    plt.imshow(cloud)

main()
