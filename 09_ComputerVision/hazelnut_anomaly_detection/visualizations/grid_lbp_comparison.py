import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import local_binary_pattern
import koreanize_matplotlib

def plot_global_vs_grid(normal_path, anomaly_path, grid_n=4, radius=1):
    """
    전역 LBP vs Grid 4×4 LBP 히스토그램 비교
    정상/이상 이미지에서 전역은 차이가 작고,
    결함이 있는 셀에서는 차이가 크다는 걸 보여줌
    """
    n_points = 8 * radius
    n_bins   = n_points + 2

    def get_gray(path):
        img = cv2.imread(path)
        img = cv2.resize(img, (256, 256))
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def lbp_hist(gray_region):
        lbp = local_binary_pattern(gray_region, n_points, radius, method='uniform')
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
        return hist

    normal_gray  = get_gray(normal_path)
    anomaly_gray = get_gray(anomaly_path)

    # ── 전역 히스토그램 ───────────────────────────────────────────
    hist_normal_global  = lbp_hist(normal_gray)
    hist_anomaly_global = lbp_hist(anomaly_gray)

    # ── Grid 4×4 히스토그램 ──────────────────────────────────────
    cell = 256 // grid_n
    hists_normal  = []
    hists_anomaly = []
    for r in range(grid_n):
        for c in range(grid_n):
            cell_n = normal_gray [r*cell:(r+1)*cell, c*cell:(c+1)*cell]
            cell_a = anomaly_gray[r*cell:(r+1)*cell, c*cell:(c+1)*cell]
            hists_normal.append(lbp_hist(cell_n))
            hists_anomaly.append(lbp_hist(cell_a))

    # ── 셀별 히스토그램 거리 (L1 거리) ───────────────────────────
    cell_diffs = [np.sum(np.abs(hists_normal[i] - hists_anomaly[i]))
                  for i in range(grid_n * grid_n)]
    global_diff = np.sum(np.abs(hist_normal_global - hist_anomaly_global))

    # ── 가장 차이 큰 셀 찾기 ──────────────────────────────────────
    most_diff_idx = int(np.argmax(cell_diffs))
    most_diff_r   = most_diff_idx // grid_n
    most_diff_c   = most_diff_idx  % grid_n

    # ── 시각화 ────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('전역 LBP vs Grid 4×4 LBP 비교', fontsize=14, fontweight='bold')

    # 원본 이미지
    normal_rgb  = cv2.cvtColor(cv2.imread(normal_path),  cv2.COLOR_BGR2RGB)
    anomaly_rgb = cv2.cvtColor(cv2.imread(anomaly_path), cv2.COLOR_BGR2RGB)
    normal_rgb  = cv2.resize(normal_rgb,  (256, 256))
    anomaly_rgb = cv2.resize(anomaly_rgb, (256, 256))

    # Grid 선 + 결함 셀 강조
    for img, ax, label in [(normal_rgb.copy(),  axes[0][0], '정상'),
                            (anomaly_rgb.copy(), axes[1][0], '이상')]:
        ax.imshow(img)
        for i in range(1, grid_n):
            ax.axhline(i * cell, color='cyan', linewidth=1)
            ax.axvline(i * cell, color='cyan', linewidth=1)
        if label == '이상':
            rect = plt.Rectangle(
                (most_diff_c * cell, most_diff_r * cell), cell, cell,
                linewidth=2, edgecolor='red', facecolor='red', alpha=0.25
            )
            ax.add_patch(rect)
            ax.set_title(f'{label} (빨간 셀 = 가장 차이 큰 셀)', fontsize=11)
        else:
            ax.set_title(label, fontsize=11)
        ax.axis('off')

    # 전역 히스토그램 비교
    x = np.arange(n_bins)
    axes[0][1].bar(x - 0.2, hist_normal_global,  0.4, color='#534AB7', alpha=0.8, label='정상')
    axes[0][1].bar(x + 0.2, hist_anomaly_global, 0.4, color='#D85A30', alpha=0.8, label='이상')
    axes[0][1].set_title(f'전역 히스토그램 (L1 거리: {global_diff:.4f})', fontsize=11)
    axes[0][1].set_xlabel('LBP bin')
    axes[0][1].set_ylabel('빈도')
    axes[0][1].legend()

    # 가장 차이 큰 셀 히스토그램 비교
    best_n = hists_normal [most_diff_idx]
    best_a = hists_anomaly[most_diff_idx]
    axes[1][1].bar(x - 0.2, best_n, 0.4, color='#534AB7', alpha=0.8, label='정상')
    axes[1][1].bar(x + 0.2, best_a, 0.4, color='#D85A30', alpha=0.8, label='이상')
    axes[1][1].set_title(
        f'가장 차이 큰 셀 ({most_diff_r},{most_diff_c}) 히스토그램\n'
        f'(L1 거리: {cell_diffs[most_diff_idx]:.4f}  vs  전역: {global_diff:.4f})',
        fontsize=11
    )
    axes[1][1].set_xlabel('LBP bin')
    axes[1][1].set_ylabel('빈도')
    axes[1][1].legend()

    # 셀별 L1 거리 히트맵
    diff_map = np.array(cell_diffs).reshape(grid_n, grid_n)
    im = axes[0][2].imshow(diff_map, cmap='hot')
    axes[0][2].set_title('셀별 히스토그램 L1 거리\n(밝을수록 차이 큼)', fontsize=11)
    axes[0][2].set_xticks(range(grid_n))
    axes[0][2].set_yticks(range(grid_n))
    for r in range(grid_n):
        for c in range(grid_n):
            axes[0][2].text(c, r, f'{diff_map[r,c]:.3f}',
                            ha='center', va='center', fontsize=8,
                            color='white' if diff_map[r,c] > diff_map.max()*0.5 else 'black')
    plt.colorbar(im, ax=axes[0][2])

    axes[1][2].axis('off')

    plt.tight_layout()
    plt.savefig('global_vs_grid.png', dpi=150, bbox_inches='tight')
    plt.show()


# 실행
plot_global_vs_grid(
    normal_path  = "../data/hazelnut/train/good/000.png",
    anomaly_path = "../data/hazelnut/test/crack/000.png"
)