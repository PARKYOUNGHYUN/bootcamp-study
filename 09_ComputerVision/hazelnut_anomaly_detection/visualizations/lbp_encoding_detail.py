import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import koreanize_matplotlib

def plot_lbp_to_histogram():
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('LBP 인코딩 → 히스토그램 bin 과정', fontsize=15, fontweight='bold', y=0.98)

    # ── ① 3×3 픽셀 그리드 ──────────────────────────────────────────
    ax1 = fig.add_subplot(1, 4, 1)
    ax1.set_title('① 픽셀 비교\n(중심=100)', fontsize=11)
    ax1.set_xlim(0, 3)
    ax1.set_ylim(0, 3)
    ax1.set_aspect('equal')
    ax1.axis('off')

    pixels = [[110, 80,  90],
              [60,  100, 130],
              [95,  70,  120]]

    for r in range(3):
        for c in range(3):
            val = pixels[r][c]
            if r == 1 and c == 1:
                color = '#534AB7'
                tc = 'white'
            elif val > 100:
                color = '#f0f0f0'
                tc = 'black'
            else:
                color = '#2c2c2a'
                tc = '#d3d1c7'
            rect = plt.Rectangle([c, 2-r], 1, 1, color=color, ec='white', lw=2)
            ax1.add_patch(rect)
            ax1.text(c+0.5, 2-r+0.6, str(val), ha='center', va='center',
                     fontsize=12, fontweight='bold', color=tc)
            bit = '' if (r==1 and c==1) else ('1' if val > 100 else '0')
            bit_color = '#7F77DD' if bit == '1' else '#888780'
            ax1.text(c+0.5, 2-r+0.25, bit, ha='center', va='center',
                     fontsize=10, color=bit_color)

    # ── ② 반시계 읽기 순서 ──────────────────────────────────────────
    ax2 = fig.add_subplot(1, 4, 2)
    ax2.set_title('② 3시→반시계 읽기\n순서 0~7', fontsize=11)
    ax2.set_xlim(-1.8, 1.8)
    ax2.set_ylim(-1.8, 1.8)
    ax2.set_aspect('equal')
    ax2.axis('off')

    # 중심
    center_circle = plt.Circle((0, 0), 0.3, color='#534AB7')
    ax2.add_patch(center_circle)
    ax2.text(0, 0, '100', ha='center', va='center', fontsize=9,
             color='white', fontweight='bold')

    # 3시에서 반시계 방향 8개 위치
    # skimage: 0=3시, 1=1시반, 2=12시, 3=10시반, 4=9시, 5=7시반, 6=6시, 7=4시반
    angles_deg = [0, 45, 90, 135, 180, 225, 270, 315]  # 반시계
    neighbor_vals = [130, 120, 80, 90, 60, 110, 70, 95]
    bits =          [1,   1,  0,  0,  0,  1,   0,  0]

    for i, (ang, val, bit) in enumerate(zip(angles_deg, neighbor_vals, bits)):
        rad = np.radians(ang)
        x = 1.2 * np.cos(rad)
        y = 1.2 * np.sin(rad)
        fc = '#f0f0f0' if bit == 1 else '#2c2c2a'
        tc = 'black' if bit == 1 else '#d3d1c7'
        circle = plt.Circle((x, y), 0.28, color=fc, ec='gray', lw=0.8)
        ax2.add_patch(circle)
        ax2.text(x, y+0.07, str(val), ha='center', va='center',
                 fontsize=8, color=tc, fontweight='bold')
        bit_color = '#534AB7' if bit == 1 else '#888780'
        ax2.text(x, y-0.1, str(bit), ha='center', va='center',
                 fontsize=9, color=bit_color, fontweight='bold')
        ax2.text(x*1.55, y*1.55, str(i), ha='center', va='center',
                 fontsize=8, color='gray')

    # 반시계 화살표
    theta = np.linspace(np.radians(30), np.radians(320), 100)
    ax2.plot(0.72*np.cos(theta), 0.72*np.sin(theta),
             color='#534AB7', lw=1, linestyle='--', alpha=0.5)
    ax2.annotate('', xy=(0.72*np.cos(np.radians(325)), 0.72*np.sin(np.radians(325))),
                 xytext=(0.72*np.cos(np.radians(315)), 0.72*np.sin(np.radians(315))),
                 arrowprops=dict(arrowstyle='->', color='#534AB7', lw=1.2))

    # ── ③ 비트코드 + uniform 판정 ──────────────────────────────────
    ax3 = fig.add_subplot(1, 4, 3)
    ax3.set_title('③ 비트코드 & uniform 판정', fontsize=11)
    ax3.axis('off')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)

    bits_list = [1, 1, 0, 0, 0, 1, 0, 0]
    ax3.text(5, 9.2, '읽은 순서대로', ha='center', fontsize=10, color='gray')

    for i, b in enumerate(bits_list):
        fc = '#f0f0f0' if b == 1 else '#2c2c2a'
        tc = 'black' if b == 1 else '#d3d1c7'
        rect = plt.Rectangle([0.8 + i*1.05, 7.8], 0.9, 0.9,
                              color=fc, ec='gray', lw=0.8)
        ax3.add_patch(rect)
        ax3.text(0.8 + i*1.05 + 0.45, 8.25, str(b),
                 ha='center', va='center', fontsize=12,
                 fontweight='bold', color=tc)
        ax3.text(0.8 + i*1.05 + 0.45, 7.55, str(i),
                 ha='center', va='center', fontsize=8, color='gray')

    ax3.text(5, 6.9, '10100100', ha='center', fontsize=14,
             fontweight='bold', color='#534AB7', family='monospace')

    # 전환 횟수 표시
    ax3.text(5, 6.1, '전환 횟수 계산 (0↔1 변화)', ha='center', fontsize=9, color='gray')

    transitions = []
    for i in range(8):
        if bits_list[i] != bits_list[(i+1) % 8]:
            transitions.append(i)

    ax3.text(5, 5.4, f'전환 위치: {len(transitions)}회', ha='center',
             fontsize=11, fontweight='bold',
             color='#D85A30' if len(transitions) > 2 else '#3B6D11')

    ax3.text(5, 4.6,
             '2회 이하 → uniform bin' if len(transitions) <= 2 else '2회 초과 → non-uniform bin',
             ha='center', fontsize=11, fontweight='bold',
             color='#3B6D11' if len(transitions) <= 2 else '#D85A30',
             bbox=dict(boxstyle='round,pad=0.4',
                       facecolor='#EAF3DE' if len(transitions) <= 2 else '#FAECE7',
                       edgecolor='none'))

    ax3.text(5, 3.5,
             f'n_points=8 → n_bins=10\n(uniform 8개 + 나머지 + 전체비율)',
             ha='center', fontsize=9, color='gray',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#f8f8f8', edgecolor='#ddd'))

    # ── ④ 히스토그램 bin +1 ─────────────────────────────────────────
    ax4 = fig.add_subplot(1, 4, 4)
    ax4.set_title('④ 히스토그램 bin +1\n(non-uniform → 마지막 bin)', fontsize=11)

    n_bins = 10
    hist = np.array([15, 8, 22, 5, 30, 3, 18, 10, 25, 12])
    colors = ['#B4B2A9'] * (n_bins - 1) + ['#D85A30']

    bars = ax4.bar(range(n_bins), hist, color=colors, edgecolor='white', linewidth=0.5)

    # 마지막 bin 강조 화살표
    ax4.annotate('+1 여기!', xy=(n_bins-1, hist[-1]), xytext=(n_bins-2.5, hist[-1]+5),
                 fontsize=9, color='#D85A30', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#D85A30', lw=1.2))

    tick_labels = [str(i) for i in range(n_bins-1)] + ['non-u']
    ax4.set_xticks(range(n_bins))
    ax4.set_xticklabels(tick_labels, fontsize=8)
    ax4.set_xlabel('bin 번호', fontsize=10)
    ax4.set_ylabel('카운트', fontsize=10)
    ax4.tick_params(axis='x', colors='gray')

    plt.tight_layout()
    plt.savefig('lbp_encoding_process.png', dpi=150, bbox_inches='tight')
    plt.show()


plot_lbp_to_histogram()