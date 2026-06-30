import koreanize_matplotlib
import matplotlib.pyplot as plt
import numpy as np
from queries import fetch_sido_accident_count

df = fetch_sido_accident_count()

# 차트 1: 지역별 보증사고 건수(막대) + 전세율(선) 이중축
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.bar(df['지역'], df['보증사고 건수 평균'], color='skyblue', label='보증사고 건수 평균', alpha=0.7)
ax1.set_xlabel('지역')
ax1.set_xticklabels(df['지역'], rotation=45)
ax1.set_ylabel('사고건수 (건)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()
ax2.plot(df['지역'], df['전세율 평균'], color='red', marker='o', linewidth=2, label='전세 실거래가율 평균 (%)')
ax2.set_ylabel('전세 실거래가율 평균 (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')
plt.title('지역별 보증사고 건수 및 실거래가율 추이')
fig.tight_layout()
plt.show()

# 차트 2: 지역별 보증사고 건수 vs 전세율 이중축 산점도
fig, ax1 = plt.subplots(figsize=(12, 6))
x = range(len(df))

sc1 = ax1.scatter(x, df['보증사고 건수 평균'], label='보증사고 건수 평균', s=100)
ax1.set_ylabel("보증사고 건수 평균")

ax2 = ax1.twinx()
sc2 = ax2.scatter(x, df['전세율 평균'], color='red', label='전세율 평균', s=100)
ax2.set_ylabel("전세율 평균")

ax1.set_xticks(x)
ax1.set_xticklabels(df['지역'], rotation=90)
ax1.legend([sc1, sc2], [sc1.get_label(), sc2.get_label()], loc='upper left')
plt.title("Deposit vs Jeonse Rate")
plt.tight_layout()
plt.show()

# 차트 3: 지역별 색상 산점도 (레이블 없음)
plt.figure(figsize=(10, 8))
colors = plt.cm.tab20(np.linspace(0, 1, len(df)))

for i, row in df.iterrows():
    plt.scatter(row['보증사고 건수 평균'], row['전세율 평균'], color=colors[i], s=120, label=row['지역'])

plt.xlabel("보증사고 건수 평균")
plt.ylabel("전세율 평균")
plt.title("지역별 보증금 vs 전세율 산점도")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# 차트 4: 지역별 색상 산점도 (지역명 레이블 포함)
plt.figure(figsize=(10, 8))
colors = plt.cm.tab20(np.linspace(0, 1, len(df)))

for i, row in df.iterrows():
    plt.scatter(row['보증사고 건수 평균'], row['전세율 평균'], color=colors[i], s=120, label=row['지역'])
    plt.text(row['보증사고 건수 평균'], row['전세율 평균'], row['지역'], fontsize=9)

plt.xlabel("보증사고 건수 평균")
plt.ylabel("전세율 평균")
plt.title("지역별 보증금 vs 전세율 산점도 (지역명 표시)")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
