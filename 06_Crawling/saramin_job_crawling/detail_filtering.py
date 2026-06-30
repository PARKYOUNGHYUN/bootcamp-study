import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

df = pd.read_csv('./data/04_merged_details_IT·웹·통신.csv', encoding='utf-8-sig')

keyword_map = {
    'DataBase': ['데이터베이스', 'db', 'DB', 'database', 'sql', 'SQL'],
    'Python': ['python', '파이썬', 'PYTHON', 'Python', 'pandas', 'numpy', '전처리', '프로세싱'],
    '시스템 프로그래밍 언어': ['C#', 'c#', 'C++', 'c++', 'c언어', 'C언어', 'Java', 'JAVA', '자바'],
    '프론트엔드': ['HTML', 'CSS', 'JavaScript', '자바스크립트', 'js', 'script'],
    '앱개발': ['android', 'Flutter', 'iOS', 'Swift'],
    '생성형 AI': ['chat GPT', '챗gpt', 'gpt', 'generative ai', '생성형', '생성형ai', '생성형AI', '생성형 AI'],
    'LLM': ['llm', 'LLM', 'nlp', 'NLP'],
    'CV': ['비전', 'CV', 'FPGA', 'opencv', 'OpenCV', '영상처리', '이미지 프로세싱', 'HALCON'],
    'KDT': ['kdt', 'KDT', '부트캠프'],
    '데이터시각화': ['시각화', '데이터시각화', '데이터 시각화', 'visualization', 'tableau', '태블로', 'bi', 'BI'],
    '자격증': ['정보처리기사', '정보처리산업기사', '사회조사분석사', 'sqld', 'SQLD', 'adsp', 'ADsP'],
    'Cloud': ['aws', 'azure', 'google cloud', 'gcp', '클라우드', '네트워크'],
    'ML/DL': ['CNN', 'big data', 'BIG DATA', '빅데이터', 'Scikit-learn', '머신러닝', 'machine learning', 'Machine Learning', 'Deep Learning', '딥러닝', 'deep learning', '객체 인식', '모델링', '기계학습', '전이', 'ML/DL', '이상탐지', '예지보전', '시계열', 'yolo', 'pytorch']
}

counter = Counter()

for text in df['content'].dropna().astype(str):
    t = text.lower()
    for main_key, related_keys in keyword_map.items():
        for sub_key in related_keys:
            counter[main_key] += t.count(sub_key.lower())

df_count = pd.DataFrame(list(counter.items()), columns=['키워드', '등장횟수'])
df_count = df_count.sort_values('등장횟수', ascending=False)
print(df_count)

plt.figure(figsize=(12, 6))
sns.barplot(data=df_count, x='키워드', y='등장횟수', hue='키워드', palette='Set3')
plt.xticks(rotation=45)
plt.title('역량 및 우대사항 주요 기술/자격증 등장 빈도')
plt.tight_layout()
plt.show()
