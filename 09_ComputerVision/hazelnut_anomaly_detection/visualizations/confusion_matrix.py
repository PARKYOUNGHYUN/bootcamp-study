import matplotlib.pyplot as plt
import numpy as np
import koreanize_matplotlib

# 1. 데이터 설정 (행: 실제, 열: 예측)
# [18, 22] -> 실제 정상인데 (정상으로 예측 18, 이상으로 예측 22)
# [21, 49] -> 실제 이상인데 (정상으로 예측 21, 이상으로 예측 49)
cm = np.array([[18, 22], 
               [21, 49]])

fig, ax = plt.subplots(figsize=(6, 5))

# 2. 히트맵 그리기 (imshow 사용)
# cmap='Pastel1'이나 'Blues' 등을 사용할 수 있습니다.
im = ax.imshow(cm, interpolation='nearest', cmap='Blues', alpha=0.8)

# 3. 눈금 및 라벨 설정
classes = ['정상', '이상']
tick_marks = np.arange(len(classes))
ax.set_xticks(tick_marks)
ax.set_xticklabels(['예측 정상', '예측 이상'], fontsize=11)
ax.set_yticks(tick_marks)
ax.set_yticklabels(['실제 정상', '실제 이상'], fontsize=11)

# 4. 각 칸에 숫자와 설명 텍스트 넣기
thresh = cm.max() / 2.  # 배경색에 따라 글자색 조절 (진한 배경엔 흰색 글자)
labels = [
    ['TN\n(정상→정상)', 'FP\n(정상→이상)'],
    ['FN\n(이상→정상)', 'TP\n(이상→이상)']
]

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        color = "white" if cm[i, j] > thresh else "black"
        # 숫자 표시
        ax.text(j, i - 0.1, format(cm[i, j], 'd'),
                ha="center", va="center",
                color=color, fontsize=16, fontweight='bold')
        # 명칭 표시 (TN, FP 등)
        ax.text(j, i + 0.15, labels[i][j],
                ha="center", va="center",
                color=color, fontsize=10)

# 5. 그래프 꾸미기
ax.set_title('Confusion Matrix 결과', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('모델의 예측 결과', fontsize=13, labelpad=15)
ax.set_ylabel('실제 데이터 라벨', fontsize=13, labelpad=15)

# 격자 선 제거
ax.grid(False)

plt.tight_layout()
plt.savefig('confusion_matrix_matplotlib.png', dpi=150)
plt.show()