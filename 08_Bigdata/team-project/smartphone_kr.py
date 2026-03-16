#%%
'''데이터_2024_스마트폰과의존실태조사

- 작성일자: 2026.03.12
- 작성자 박영현
'''

#%%
import pandas as pd

#%%
extract_columns = ['Q11A1',
                     'Q11A2',
                     'Q11A3',
                     'Q11B1',
                     'Q11B2',
                     'Q11B3',
                     'Q12A1',
                     'Q12A2',
                     'Q12A3',
                     'Q33',
                     'Q71',
                     'Q72',
                     'Q71A',
                     'Q72A',
                     'Q73A',
                     'Q141']

def change_columns(df):
    df_cols_map = {col: col.replace('_', '') for col in df.columns}
    df = df.rename(columns=df_cols_map)
    return df

#%%
answer_df = pd.read_excel('./data/2024_smartphone_data.xlsx')
answer_df.head()

#%%
data_codebook = pd.read_excel('./data/2024_smartphone_data_codebook.xlsx', sheet_name='VAL')
data_codebook = data_codebook.ffill()
data_codebook.head()

#%%
data_codebook2 = pd.read_excel('./data/2024_smartphone_data_codebook.xlsx', sheet_name='VAR', header=1)
data_codebook2.head()

#%% [markdown]
# ### 여기서 부터 수정 가능 

#%%
# Q1_1A_1	[1. 스마트폰 이용현황] [문1-1] 생활에 도움이 되는 콘텐츠 (1순위)
# Q1_1A_2	[1. 스마트폰 이용현황] [문1-1] 생활에 도움이 되는 콘텐츠 (2순위)
# Q1_1A_3	[1. 스마트폰 이용현황] [문1-1] 생활에 도움이 되는 콘텐츠 (2순위)
# Q1_1B_1	[1. 스마트폰 이용현황] [문1-1] 부작용으로 걱정되는 콘텐츠 (1순위)
# Q1_1B_2	[1. 스마트폰 이용현황] [문1-1] 부작용으로 걱정되는 콘텐츠 (2순위)
# Q1_1B_3	[1. 스마트폰 이용현황] [문1-1] 부작용으로 걱정되는 콘텐츠 (3순위)
# Q1_2A_1	[1. 스마트폰 이용현황] [문1-2] 이용량이 증가한 콘텐츠 (1순위)
# Q1_2A_2	[1. 스마트폰 이용현황] [문1-2] 이용량이 증가한 콘텐츠 (2순위)
# Q1_2A_3	[1. 스마트폰 이용현황] [문1-2] 이용량이 증가한 콘텐츠 (3순위)
# Q3_3	[1. 스마트폰 이용현황] [문3] SNS 이용시간 조절에 대한 어려움
# Q7_1	[2. 온라인 동영상 서비스 이용현황] [문7] 스마트폰을 통해 이용하고 있는 숏폼 플랫폼 (1순위)
# Q7_2	[2. 온라인 동영상 서비스 이용현황] [문7] 스마트폰을 통해 이용하고 있는 숏폼 플랫폼 (2순위)
# Q7_1A	[2. 온라인 동영상 서비스 이용현황] [문7-1] 숏폼이 온라인동영상 서비스 이용에서 차지하는 비중
# Q7_2A	[2. 온라인 동영상 서비스 이용현황] [문7-2] 본인의 의지대로 숏폼 시청을 조절하는 것에 느끼는 어려움
# Q7_3A	[2. 온라인 동영상 서비스 이용현황] [문7-3] AI의 추천 알고리즘에 의해 같은 유형의 숏폼 콘텐츠를 반복해서 보게 된다
# Q14_1	[4. 과의존 문제해결에 관한 인식] [문14] 심층경험 여부_시간 가는줄 모르고 숏폼, SNS 게시물을 보다가 예상보다 장시간 이용한 적이 있다

answer_df = change_columns(answer_df)
#print(answer_df.columns)
extract_answer_data = answer_df[extract_columns]
extract_answer_data.head()

##%%
#print(extract_answer_data.shape)
#print(extract_answer_data.dtypes)
#print(extract_answer_data.describe())
#
##%%
#print(extract_answer_data['Q72A'].value_counts())  # 숏폼 조절 어려움
#print(extract_answer_data['Q73A'].value_counts())  # AI 알고리즘 반복 시청
#print(extract_answer_data['Q33'].value_counts())   # SNS 이용시간 조절 어려움

#%%

# '변수값'라는 열에서 '_'를 제거하고 싶은 경우
data_codebook['변수값'] = data_codebook['변수값'].str.replace('_', '', regex=False)
data_codebook = data_codebook.rename(columns={'Unnamed: 1': '값', 'Unnamed: 2': '라벨'})
extract_data_codebook =  data_codebook[data_codebook['변수값'].isin(extract_columns)]
extract_data_codebook
#questions = data_codebook['변수값'].unique().tolist()
#questions

#%%
data_codebook2['변수'] = data_codebook2['변수'].str.replace('_', '', regex=False)
data_codebook2 =  data_codebook2[data_codebook2['변수'].isin(extract_columns)]
data_codebook2

#%%
extract_data_codebook['값'] = extract_data_codebook['값'].astype(str)

#%%
# 변수별 매핑 딕셔너리 생성
mapping = {}
for var in extract_columns:
    temp = extract_data_codebook[extract_data_codebook['변수값'] == var].set_index('값')['라벨'].to_dict()
    mapping[var] = temp
mapping['Q141']

#%%
# 데이터에 라벨 적용
for var in extract_columns:
    if var in answer_df.columns:
        answer_df[var] = answer_df[var].astype('Int64').fillna(answer_df[var])
        answer_df[var] = answer_df[var].astype('str')
        answer_df[f'{var}_라벨'] = answer_df[var].map(mapping[var])

#print(answer_df.columns)

#%%
# A컬럼을 Key로, B컬럼을 Value로 변환
result_dict = dict(zip(data_codebook2['변수'], data_codebook2['레이블']))
result_dict

for column in extract_columns:
    print(f"\n{'='*50}")
    print(f"컬럼: {column}")
    print(f"질문: {result_dict.get(column, '질문 없음')}")
    
    # 0명 포함한 전체 카운트 만들기
    counts = []
    for val, label in sorted(mapping[column].items()):
        count = (answer_df[column] == val).sum()
        counts.append({'index': val, 'answer': label, 'count': count})
    
    count_df = pd.DataFrame(counts)
    print(count_df)
    
    # CSV 저장 (0명 포함)
    count_df.to_csv(f'./data/output/{result_dict[column]}.csv', index=False)
