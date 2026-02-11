import koreanize_matplotlib
import matplotlib.pyplot as plt
from queries import fetch_yearly_accident_unsold

df = fetch_yearly_accident_unsold()
df['연도'] = df['연도'].astype(str)

fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.bar(df['연도'], df['보증건수 평균'], color='skyblue', label='보증건수 평균', alpha=0.7)
ax1.set_xticks(range(len(df['연도'])))
ax1.set_xlabel('연도')
ax1.set_xticklabels(df['연도'])
ax1.set_ylabel('사고건수 (건)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()
ax2.plot(df['연도'], df['미분양 평균'], color='red', marker='o', linewidth=2, label='미분양 평균')
ax2.set_ylabel('미분양 평균', color='red')
ax2.tick_params(axis='y', labelcolor='red')

lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')
plt.title('연도별 보증사고 건수 및 미분양 평균 추이')
fig.tight_layout()
plt.show()
