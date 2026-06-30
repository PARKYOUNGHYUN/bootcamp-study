import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from skimage.feature import local_binary_pattern
import koreanize_matplotlib


# ── 1. LBP 인코딩 원리 시각화 ────────────────────────────────────────────
def plot_lbp_concept():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    pixels = np.array([[80, 120, 90],
                       [60,  100, 130],
                       [110, 70,  95]])
    center = pixels[1, 1]

    # 원본 픽셀 그리드
    axes[0].imshow(pixels, cmap='gray', vmin=0, vmax=255)
    for i in range(3):
        for j in range(3):
            color = 'red' if (i == 1 and j == 1) else 'white'
            axes[0].text(j, i, str(pixels[i, j]), ha='center', va='center',
                         fontsize=14, fontweight='bold', color=color)
    axes[0].set_title('원본 픽셀 밝기값\n(빨강=중심)', fontsize=12)
    axes[0].axis('off')

    # 이진화 결과 (이웃 > 중심 → 1)
    binary = (pixels > center).astype(int)
    display = binary.astype(float)
    display[1, 1] = 0.5  # 중심 구분용

    axes[1].imshow(display, cmap='RdYlGn', vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                axes[1].text(j, i, 'c', ha='center', va='center',
                             fontsize=14, fontweight='bold', color='black')
            else:
                axes[1].text(j, i, str(binary[i, j]), ha='center', va='center',
                             fontsize=14, fontweight='bold', color='black')
    axes[1].set_title('이진화\n(이웃 > 중심 → 1)', fontsize=12)
    axes[1].axis('off')

    # LBP 코드 설명
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].text(0.5, 0.85, '시계 방향으로 읽기', ha='center', fontsize=12)
    axes[2].text(0.5, 0.65, '1 → 1 → 0 → 1 → 0 → 0 → 0 → 1',
                 ha='center', fontsize=11, family='monospace',
                 bbox=dict(boxstyle='round', facecolor='#e8f4f8', alpha=0.8))
    axes[2].text(0.5, 0.45, '→ LBP 코드 → 히스토그램 bin',
                 ha='center', fontsize=11, fontweight='bold', color='#2196F3')
    axes[2].text(0.5, 0.25, 'n_bins = n_points + 2 (uniform LBP 이론값)',
                 ha='center', fontsize=10, color='gray')
    axes[2].axis('off')
    axes[2].set_title('LBP 코드 생성', fontsize=12)

    plt.suptitle('LBP (Local Binary Pattern) 인코딩 원리', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('lbp_concept.png', dpi=150, bbox_inches='tight')
    plt.show()


# ── 2. 4×4 Grid 분할 시각화 ──────────────────────────────────────────────
def plot_grid_split(image_path, grid_n=4):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (256, 256))

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].imshow(img)
    axes[0].set_title('원본 이미지 (256×256)', fontsize=13)
    axes[0].axis('off')

    axes[1].imshow(img)
    cell = 256 // grid_n
    for i in range(1, grid_n):
        axes[1].axhline(i * cell, color='cyan', linewidth=1.5)
        axes[1].axvline(i * cell, color='cyan', linewidth=1.5)
    for r in range(grid_n):
        for c in range(grid_n):
            axes[1].text(c * cell + cell // 2, r * cell + cell // 2,
                         f'({r},{c})', ha='center', va='center',
                         fontsize=7, color='yellow',
                         bbox=dict(facecolor='black', alpha=0.4, pad=1))
    axes[1].set_title(f'4×4 Grid 분할 (16개 셀, 각 {cell}×{cell}px)', fontsize=13)
    axes[1].axis('off')

    plt.suptitle('Grid 분할 — 결함 위치 정보 반영', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('grid_split.png', dpi=150, bbox_inches='tight')
    plt.show()


# ── 3. 멀티스케일 LBP 히스토그램 비교 ────────────────────────────────────
def plot_multiscale_lbp(normal_path, anomaly_path):
    radii  = [1, 2, 3]
    titles = ['반지름 1\n(긁힘, 미세)', '반지름 2\n(균열, 패임)', '반지름 3\n(변형, 깨짐)']
    colors = ['#2196F3', '#4CAF50', '#FF5722']

    fig, axes = plt.subplots(2, 3, figsize=(14, 7))

    for col, (radius, title, color) in enumerate(zip(radii, titles, colors)):
        for row, (path, label) in enumerate([(normal_path, '정상'), (anomaly_path, '이상')]):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (256, 256))
            n_points = 8 * radius
            lbp = local_binary_pattern(img, n_points, radius, method='uniform')
            n_bins = n_points + 2
            hist, _ = np.histogram(lbp.ravel(), bins=n_bins,
                                   range=(0, n_bins), density=True)
            ax = axes[row][col]
            ax.bar(range(n_bins), hist, color=color, alpha=0.7, width=0.8)
            ax.set_title(f'{label} — {title}', fontsize=11)
            ax.set_xlabel('LBP 패턴 bin')
            ax.set_ylabel('빈도 (확률)')
            ax.set_xlim(0, n_bins)

    plt.suptitle('멀티스케일 LBP 히스토그램 비교 (정상 vs 이상)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('multiscale_lbp.png', dpi=150, bbox_inches='tight')
    plt.show()


# ── 4. 성능 개선 단계별 시각화 ───────────────────────────────────────────
def plot_improvement():
    # 최종 코드(단일 모델, 65%ile) 기준 수치
    labels    = ['초기\n(단일 LBP\n5%ile)', 'Grid 4×4\n추가', '256×256\n크기 변경', '최종\n(65%ile)']
    f1_scores = [0.333,                      0.559,             0.705,               0.727]
    recalls   = [0.21,                       0.47,              0.79,                0.86]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width/2, f1_scores, width, label='Anomaly F1',
                   color='#2196F3', alpha=0.85)
    bars2 = ax.bar(x + width/2, recalls,   width, label='Anomaly Recall',
                   color='#4CAF50', alpha=0.85)

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=10)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('Score', fontsize=12)
    ax.legend(fontsize=11)
    ax.axhline(0.5, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_title('성능 개선 단계별 변화 (F1  0.333 → 0.727)',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('improvement.png', dpi=150, bbox_inches='tight')
    plt.show()


# ── 5. Threshold 실험 결과 ────────────────────────────────────────────────
def plot_threshold_experiment():
    percentiles = [5,     15,    50,    52,    60,    65,    70,    75]
    f1_scores   = [0.333, 0.358, 0.705, 0.721, 0.735, 0.765, 0.756, 0.754]
    recalls     = [0.21,  0.24,  0.79,  0.83,  0.87,  0.93,  0.93,  0.94]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.plot(percentiles, f1_scores, 'o-', color='#2196F3',
             linewidth=2, markersize=8, label='Anomaly F1')
    ax2.plot(percentiles, recalls,   's--', color='#FF5722',
             linewidth=2, markersize=8, label='Anomaly Recall')

    best_idx = f1_scores.index(max(f1_scores))
    ax1.axvline(percentiles[best_idx], color='gold', linestyle='--',
                linewidth=2, alpha=0.8, label=f'최적: {percentiles[best_idx]}%ile')
    ax1.scatter([percentiles[best_idx]], [f1_scores[best_idx]],
                s=200, color='gold', zorder=5)

    ax1.set_xlabel('Threshold Percentile (%)', fontsize=12)
    ax1.set_ylabel('Anomaly F1', color='#2196F3', fontsize=12)
    ax2.set_ylabel('Anomaly Recall', color='#FF5722', fontsize=12)
    ax1.set_title('Threshold Percentile 실험 결과', fontsize=14, fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=10)

    plt.tight_layout()
    plt.savefig('threshold_experiment.png', dpi=150, bbox_inches='tight')
    plt.show()


# ── 실행 ─────────────────────────────────────────────────────────────────
plot_lbp_concept()
plot_improvement()
plot_threshold_experiment()

# 이미지 경로가 있을 때
# plot_grid_split("./data/hazelnut/train/good/000.png")
# plot_multiscale_lbp("./data/hazelnut/train/good/000.png",
#                     "./data/hazelnut/test/crack/000.png")