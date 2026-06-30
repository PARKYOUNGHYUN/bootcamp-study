import matplotlib.pyplot as plt
import numpy as np
import koreanize_matplotlib
from matplotlib.patches import Patch

percentiles   = [40,    45,    50,    65]
f1_scores      = [0.686, 0.695, 0.705, 0.765]
normal_recall = [0.45,  0.45,  0.23,  0.12]
fn_counts      = [22,    21,    15,    5]

labels = [f'{p}%ile' for p in percentiles]
x = np.arange(len(percentiles))

# 색상을 지표별로 통일 (강조 색상 하나로 고정)
bar_colors = {
    'f1':     '#AFA9EC',
    'recall': '#9FE1CB',
    'fn':     '#F5C4B3',
}

fig, ax1 = plt.subplots(figsize=(10, 6)) # 하단 범례 공간을 위해 높이를 조금 늘림
fig.suptitle('Threshold Percentile 실험 결과', fontsize=14, fontweight='bold')

width = 0.25
ax2 = ax1.twinx()
ax2.get_yaxis().set_visible(False)

# 막대 생성 (모두 동일한 색상 적용)
bars1 = ax1.bar(x - width, f1_scores,     width, color=bar_colors['f1'])
bars2 = ax1.bar(x,         normal_recall, width, color=bar_colors['recall'])
bars3 = ax2.bar(x + width, fn_counts,     width, color=bar_colors['fn'])

ax1.set_ylim(0, 1.0)
ax2.set_ylim(0, 30)
ax1.get_yaxis().set_visible(False)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=11)

# 수치 텍스트 추가
for bar, val in zip(bars1, f1_scores):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{val:.3f}', ha='center', va='bottom', fontsize=9)
for bar, val in zip(bars2, normal_recall):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{val:.2f}', ha='center', va='bottom', fontsize=9)
for bar, val in zip(bars3, fn_counts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             str(val), ha='center', va='bottom', fontsize=9)

# 범례 설정 (3개 항목만 남기고 하단으로 이동)
legend_items = [
    Patch(facecolor= '#AFA9EC', label='Anomaly F1'),
    Patch(facecolor= '#9FE1CB', label='Normal Recall'),
    Patch(facecolor= '#F5C4B3', label='FN 수 (이상을 정상으로 잘못 예측)'),
]

# ncol=3으로 설정하여 가로로 나열, bbox_to_anchor로 하단 배치
ax1.legend(handles=legend_items, 
           loc='upper center', 
           bbox_to_anchor=(0.5, -0.15), 
           ncol=3, 
           fontsize=10, 
           frameon=False)

# 하단 공간 확보를 위해 여백 조정
plt.tight_layout()
plt.subplots_adjust(bottom=0.2) 

plt.savefig('threshold_experiment_bottom_legend.png', dpi=150, bbox_inches='tight')
plt.show()