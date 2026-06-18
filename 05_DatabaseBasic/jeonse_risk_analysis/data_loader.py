import pandas as pd
from config import get_engine

CSV_PATH = './data/data.csv'

df = pd.read_csv(CSV_PATH)
print(df.head())

engine = get_engine()
df.to_sql('jeonse_deposit_accidents', con=engine, if_exists='append', index=False)
print(f"데이터 적재 완료: {len(df)}건")
