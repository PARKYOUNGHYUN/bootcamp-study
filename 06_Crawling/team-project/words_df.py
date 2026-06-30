import pandas as pd

words_by_category = {
    '공통 기술 및 핵심 역량': ['AI', '인공지능', '빅데이터'],
    '비즈니스 및 실무 프로세스': ['기획', '분석', '서비스', '개발', '모델', '실무', '경험', '현장', '취업',
                               '인재상', '훈련', '커리큘럼', '기업수요', '맞춤형', '환경', '요구사항', '진행',
                               '도메인', '선정', '과학적', '방법론', '프로세스', '결과', '도출', 'KDT', '부트캠프'],
    '소프트웨어 개발 기초': ['파이썬', 'Python', '프로그래밍', 'Programming', '타입', '함수', '제어문',
                           '모듈', '패키지', '기초', 'Fundamentals', '파일', '저장'],
    '웹 아키텍처 및 서비스 구현': ['웹', 'Web', '서버', 'Server', '구조', '동작', '원리', '클라이언트',
                                'Client', '구현', '연동', '시스템'],
    '데이터베이스 및 SQL': ['데이터베이스', 'Database', 'DB', '관계형', 'Relational', 'RDBMS', '관리',
                          'System', 'SQL', 'Structured', 'Query', 'Language', 'DDL', 'Data',
                          'Definition', 'DML', 'Manipulation', 'JOIN', 'SUB-QUERY', '서브', '쿼리',
                          '생성', '정의', '조작', '제어', '설계', '모델링', '표준화', '전환'],
    '데이터 분석': ['데이터', '분석', 'Series', 'DataFrame', '데이터프레임', '판다스', 'Pandas', 'EDA',
                   'Exploratory', '탐색적', '수집', 'Collection', '처리', 'Processing', '전처리',
                   '시각화', '대시보드', '통계', '차원', '배열', 'Ndarray', 'N-dimensional', 'Array',
                   '상관분석', '회귀분석', '추론적', '지표', '성능평가'],
    '머신러닝': ['머신러닝', 'Machine', 'Learning', 'ML', '기계학습', '학습', '지도학습', '비지도학습', '튜닝'],
    '딥러닝': ['딥러닝', 'Deep', 'Tensor', '인공신경망', 'Neural', 'Network', 'DNN', 'CNN',
              'Convolutional', 'RNN', 'Recurrent', 'LSTM', 'Long', 'Short-Term', 'Memory',
              'GAN', 'Generative', 'Adversarial', 'Transformer', 'Transfer', '전이'],
    '시각 지능 및 이미지 처리': ['컴퓨터', 'Computer', '비전', 'Vision', '이미지', '프로세싱', '연산',
                              '이진화', '변환', '윤곽선', '특징', '매칭', '검출', 'YOLO', 'You',
                              'Only', 'Look', 'Once', '객체', '인식'],
    '언어 지능 및 텍스트 분석': ['자연어', 'NLP', 'Natural', '텍스트', '감성', '생성', '기반', '과정',
                              '순환', 'Hugging', 'Face', 'LLM', 'Large Language Model'],
    '클라우드 인프라 및 가상화': ['클라우드', 'Cloud-based', '도커', 'Docker', '개발환경', '구축', '연결', '통합'],
    '직무 인증 및 전문 자격': ['정보처리기사', '정보처리산업기사', '빅데이터분석기사', '사회조사분석사',
                            'SQLD', 'ADsP', 'Advanced', 'Analytics', 'Semi-Professional', '개발자', '준전문가']
}

df = pd.DataFrame.from_dict(words_by_category, orient='index').transpose()
df.to_csv('./data/03_채용 공고 매칭 역량 키워드 리스트.csv', na_rep='', index=False)
print(df.head())
