# %% [markdown]
# # 산업 이상 탐지 실습 노트북 (정확도 개선판)
# ## MVTec AD `hazelnut` + **멀티스케일 LBP** + **Isolation Forest** + OpenCV 후처리
#
# ### 제약 조건
# - 특징 추출: **LBP만 사용** (HOG, 색상 히스토그램 등 사용 안 함)
# - 모델: **Isolation Forest 앙상블 (3개 random_state 평균)**
#
# ### 개선 항목
# | 항목 | 기존 | 개선 |
# |------|------|------|
# | 이미지 전처리 | Blur → CLAHE | 원본 Grayscale (미세 결함 패턴 보존) |
# | LBP 추출 | 전역 단일 스케일 | 4×4 Grid × 반지름 [1,2,3] 멀티스케일 |
# | 정규화 | StandardScaler | 제거 (LBP 히스토그램은 이미 확률 분포) |
# | 모델 | 단일 IF (n=300) | IF 앙상블 3개 (n=500, max_samples=0.8) |
# | Threshold | train 하위 5% 고정 | validation 중앙값(65%ile, 누수 없음) |
# | 이미지 크기 | 128×128 | 256×256 (미세 균열 LBP 소실 방지) |
# | 이상 위치 이진화 | Otsu | THRESH_TRIANGLE (단봉 분포 대응) |
# | Morphology | OPEN → CLOSE | OPEN → DILATE → CLOSE (박스 안정성 강화) |

# %% [markdown]
# ## 1. 라이브러리 설치

# %%
# !pip -q install scikit-image scikit-learn opencv-python matplotlib koreanize-matplotlib

# %% [markdown]
# ## 2. 모듈 import

# %%
import koreanize_matplotlib
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

from skimage.feature import local_binary_pattern
from skimage.metrics import structural_similarity as ssim

from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_curve, auc, f1_score
)

# %% [markdown]
# ## 3. 경로 및 전역 상수 설정
#
# CLAHE 객체는 모듈 상단에서 한 번만 생성하고 재사용합니다.
# 이미지 수백 장을 처리할 때 함수 호출마다 생성하는 낭비를 방지합니다.

# %%
DATASET_DIR = "./data/hazelnut"
IMG_SIZE    = (256, 256)   # 특징 추출용 크기 — 고해상도로 미세 균열의 LBP 소실 방지
LOC_SIZE    = (256, 256)   # 이상 위치 표시용 크기
MIN_AREA    = 100          # 이상 위치 박스 최소 면적 (픽셀 단위)

# CLAHE 객체 전역 1회 생성
# → extract_lbp_feature, build_mean_reference, localize_anomaly 세 곳에서 공유
CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# %% [markdown]
# ## 4. 전처리 + Grid 멀티스케일 LBP 특징 추출 함수
#
# ### 원본 Grayscale (전처리)
# LBP는 픽셀 간 밝기 대소를 비교해 패턴을 만듭니다.
# Blur나 CLAHE는 미세 균열·긁힘의 고주파 경계를 뭉개
# LBP가 포착해야 할 결함 패턴을 약화시키므로 적용하지 않습니다.
# 원본 픽셀 대조값을 그대로 보존해 결함 패턴이 히스토그램에 명확히 반영되게 합니다.
#
# ### n_bins 이론값 고정
# `uniform` LBP의 가능한 패턴 수는 `n_points + 2`로 이론적으로 고정되므로
# 이 값을 n_bins로 사용하면 모든 이미지에서 벡터 길이가 항상 동일합니다.
#
# ### Grid 분할 LBP (4×4 격자)
# 전역 히스토그램은 결함이 어디에 있든 같은 벡터를 만들어 위치 정보가 소실됩니다.
# 이미지를 4×4 격자(16개 셀)로 나눠 셀마다 히스토그램을 추출하면
# 결함의 위치 정보가 특징 벡터에 반영됩니다.
# 셀이 작을수록 결함이 해당 셀 히스토그램에서 차지하는 밀도가 커져
# 미세 결함이 특징에 더 명확히 드러납니다.
# (256×256 기준 각 셀 = 64×64 픽셀)
#
# ### 멀티스케일 LBP (반지름 1·2·3)
# - 반지름 1: 미세 텍스처 (긁힘, 미세 오염)
# - 반지름 2: 중간 텍스처 (균열, 패인 흔적)
# - 반지름 3: 거시 텍스처 (큰 변형, 깨짐)
#
# 최종 특징 벡터 = 16 셀 × 3 스케일 × (n_points + 2) bins

# %%
# Grid 분할 수 (GRID_N × GRID_N 개 셀)
# 4×4 격자: 16개 셀로 분할해 미세 결함이 히스토그램에서 차지하는 비중을 높임
# 셀이 작을수록 결함이 전체 픽셀에서 차지하는 밀도가 커져 특징에 더 명확히 반영됨
GRID_N = 4

# 멀티스케일 LBP 반지름 목록
# radius=5 는 64×64 셀 환경에서도 노이즈 bin을 늘려 판별력을 저하시키므로 제거
LBP_RADII = [1, 2, 3]

def extract_lbp_feature(image_path, size=(128, 128)):
    """
    이미지 1장에서 Grid 분할 멀티스케일 LBP 히스토그램을 추출합니다.

    처리 순서
    ---------
    1) 이미지 읽기 → resize
    2) 원본 Grayscale 변환 (전처리 없음)
    3) GRID_N×GRID_N 격자 분할
    4) 각 셀 × 각 반지름(LBP_RADII)마다 LBP 히스토그램 추출
    5) 전체 히스토그램 이어 붙여 반환

    반환값
    ------
    feature      : 1차원 복합 LBP 특징 벡터
    original_rgb : 시각화용 원본 RGB 이미지
    gray         : 분석용 흑백 이미지 (원본 그대로)
    """
    img = cv2.imread(image_path)
    if img is None:
        return None, None, None

    original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(img, size)

    # ── 원본 Grayscale 변환 ──────────────────────────────────────
    # LBP는 픽셀 간 밝기 대소를 비교해 패턴을 만듭니다.
    # Blur나 CLAHE는 미세 균열·긁힘 같은 고주파 경계를 뭉개
    # LBP가 포착해야 할 결함 패턴을 약화시킵니다.
    # 원본 픽셀 대조값을 보존하기 위해 전처리 없이 바로 Grayscale 변환합니다.
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape
    cell_h = h // GRID_N
    cell_w = w // GRID_N

    # ── Grid 분할 멀티스케일 LBP ─────────────────────────────────
    all_hists = []
    for row in range(GRID_N):
        for col in range(GRID_N):
            # 셀 영역 추출
            cell = gray[
                row * cell_h : (row + 1) * cell_h,
                col * cell_w : (col + 1) * cell_w
            ]
            for radius in LBP_RADII:
                n_points = 8 * radius
                lbp = local_binary_pattern(cell, n_points, radius, method='uniform')
                n_bins = n_points + 2      # uniform LBP 이론값 고정
                hist, _ = np.histogram(
                    lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True
                )
                all_hists.append(hist)

    feature = np.concatenate(all_hists)
    return feature, original_rgb, gray

# %% [markdown]
# ## 5. 정상 학습 이미지 특징 추출

# %%
train_good_dir = os.path.join(DATASET_DIR, "train", "good")

X_train_raw = []
train_paths  = []

for fname in sorted(os.listdir(train_good_dir)):
    fpath = os.path.join(train_good_dir, fname)
    feat, _, _ = extract_lbp_feature(fpath, IMG_SIZE)
    if feat is not None:
        X_train_raw.append(feat)
        train_paths.append(fpath)

X_train_raw = np.array(X_train_raw)
print(f"정상 학습 이미지 수   : {len(X_train_raw)}")
print(f"원본 특징 벡터 shape : {X_train_raw.shape}")

# %% [markdown]
# ## 6. 학습 이미지 일부 확인
#
# 특징 추출 직후, 모델 학습 전에 실제 학습 데이터를 눈으로 먼저 확인합니다.

# %%
sample_count = min(6, len(train_paths))
plt.figure(figsize=(12, 6))
for i in range(sample_count):
    img = cv2.imread(train_paths[i])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.subplot(2, 3, i + 1)
    plt.imshow(img)
    plt.title(f"train/good 예시 {i+1}")
    plt.axis("off")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7. Train / Validation 분리
#
# Threshold를 정하려면 '정답을 모르는' 기준 데이터가 필요합니다.
# 테스트 레이블(`y_true`)을 쓰면 정답을 미리 본 것과 같아 성능이 부풀려집니다.
# 대신 **정상 학습 데이터를 80/20으로 분리**하여
# 20%(validation)의 점수로 threshold를 결정하고,
# 80%(train)로만 모델을 학습합니다.
# 이렇게 하면 threshold 탐색 과정에서 테스트 레이블이 전혀 개입하지 않습니다.

# %%
X_tr_raw, X_val_raw = train_test_split(
    X_train_raw, test_size=0.2, random_state=42
)
print(f"Train  : {len(X_tr_raw)}장")
print(f"Val    : {len(X_val_raw)}장")

# %% [markdown]
# ## 8. 정규화 제거 — Raw 히스토그램 사용
#
# LBP 히스토그램은 `density=True` 옵션으로 이미 합이 1인 확률 분포입니다.
# Isolation Forest는 트리 기반 모델이라 스케일에 무관합니다.
# StandardScaler는 오히려 빈도 낮은 이상치 bin을 과도하게 증폭시킬 수 있으므로 제거합니다.

# %%
# 정규화 없이 원본 특징 벡터를 그대로 사용
X_tr  = X_tr_raw
X_val = X_val_raw

print(f"Train shape : {X_tr.shape}")
print(f"Val   shape : {X_val.shape}")

# %% [markdown]
# ## 9. Isolation Forest 앙상블 학습 (Ensemble Voting)
#
# ### 왜 앙상블인가?
# Isolation Forest는 랜덤 분할을 사용하므로 `random_state` 하나에 의존하면
# 특정 트리 집합의 편향(Bias)이 결과에 영향을 줄 수 있습니다.
# 서로 다른 `random_state`를 가진 모델 3개를 학습한 뒤
# `decision_function` 점수를 평균하면 편향이 상쇄되고
# 결정 경계가 더 안정적으로 형성됩니다.

# %%
RANDOM_STATES = [42, 123, 7]   # 앙상블에 사용할 random_state 목록

models = []
for rs in RANDOM_STATES:
    m = IsolationForest(
        n_estimators=500,
        # 300 → 500: 트리를 더 많이 심어 복잡한 결정 경계를 세밀하게 구축
        contamination='auto',
        # contamination 은 decision_function 의 offset_ 을 결정하지만,
        # 이 코드는 percentile 기반 threshold 를 사용하므로 실질적 영향이 적습니다.
        # 'auto' 는 offset_ = -0.5 로 설정하며 가장 중립적인 선택입니다.
        max_features=1.0,
        # 격자 분할 시 결함이 특정 셀에만 존재합니다.
        # max_features=0.5 면 해당 셀의 특징이 선택되지 않을 수 있으므로
        # 전체 특징(1.0)을 사용해 결함 셀 정보가 반드시 반영되게 합니다.
        max_samples=0.8,
        # 각 트리가 전체 학습 데이터의 80%를 무작위로 보게 하여
        # 트리 간 다양성을 높이고 일반화 성능을 향상시킵니다.
        random_state=rs
    )
    m.fit(X_tr)
    models.append(m)

print(f"앙상블 모델 {len(models)}개 학습 완료 (random_states={RANDOM_STATES})")


def ensemble_score(X_input):
    """모델 3개의 decision_function 점수를 평균합니다."""
    scores = np.array([m.decision_function(X_input) for m in models])
    return scores.mean(axis=0)

# %% [markdown]
# ## 10. 테스트 데이터 특징 추출

# %%
test_dir = os.path.join(DATASET_DIR, "test")

X_test_raw   = []
y_true       = []
test_paths   = []
defect_types = []

for defect_type in sorted(os.listdir(test_dir)):
    defect_path = os.path.join(test_dir, defect_type)
    if not os.path.isdir(defect_path):
        continue
    for fname in sorted(os.listdir(defect_path)):
        fpath = os.path.join(defect_path, fname)
        feat, _, _ = extract_lbp_feature(fpath, IMG_SIZE)
        if feat is not None:
            X_test_raw.append(feat)
            test_paths.append(fpath)
            defect_types.append(defect_type)
            y_true.append(0 if defect_type == "good" else 1)

X_test_raw = np.array(X_test_raw)
y_true     = np.array(y_true)

print(f"테스트 이미지 수 : {len(X_test_raw)}")
print(f"정상 수          : {np.sum(y_true == 0)}")
print(f"이상 수          : {np.sum(y_true == 1)}")

# %% [markdown]
# ## 11. 앙상블 점수 계산

# %%
X_test = X_test_raw   # 정규화 없이 원본 사용

val_scores  = ensemble_score(X_val)
test_scores = ensemble_score(X_test)

print("validation 앙상블 점수 일부:", np.round(val_scores[:10], 4))

# %% [markdown]
# ## 12. Threshold 설정 — validation 점수 하위 65% (중앙값)
#
# - 모델은 train(80%)으로만 학습
# - Threshold는 **validation(20%) 점수의 중앙값(65%ile)** 으로 결정
#   - "정상 점수의 절반 아래이면 이상"으로 간주해 민감도를 높입니다
#   - recall이 크게 향상되지만 정상 오탐(False Positive)도 증가합니다
#   - 테스트 레이블(`y_true`)은 이 과정에 전혀 개입하지 않음

# %%
threshold = np.percentile(val_scores, 65)
print(f"Threshold (val 하위 65%, 중앙값) : {threshold:.4f}")

# validation 점수 분포 시각화
plt.figure(figsize=(7, 4))
plt.hist(val_scores, bins=20, color='steelblue', edgecolor='white', label='Val 점수')
plt.axvline(threshold, color='red', linestyle='--', label=f'Threshold = {threshold:.3f}')
plt.xlabel('Decision Score')
plt.ylabel('빈도')
plt.title('Validation 점수 분포 및 Threshold (중앙값 65%)')
plt.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 13. 정상/이상 판별 및 성능 평가

# %%
y_pred = (test_scores < threshold).astype(int)

print("Confusion Matrix")
print(confusion_matrix(y_true, y_pred))
print()
print("Classification Report")
print(classification_report(y_true, y_pred, target_names=["normal", "anomaly"]))
print(f"Anomaly F1-score : {f1_score(y_true, y_pred):.4f}")

# ROC AUC는 threshold와 무관하게 모델 자체의 판별력을 나타내므로 참고용으로 출력
fpr, tpr, _ = roc_curve(y_true, -test_scores)
roc_auc = auc(fpr, tpr)
print(f"ROC AUC (참고용) : {roc_auc:.4f}")

plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, color='steelblue', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', lw=1)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC 곡선 (참고용)')
plt.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 14. 결과 시각화
#
# 제목 초록: 정답 / 빨강: 오답

# %%
def show_results(paths, scores, labels_true, labels_pred, type_labels, threshold, n=12):
    count = min(n, len(paths))
    idxs  = np.linspace(0, len(paths) - 1, count, dtype=int)
    plt.figure(figsize=(16, 12))
    for i, idx in enumerate(idxs, 1):
        img = cv2.imread(paths[idx])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gt    = "정상" if labels_true[idx] == 0 else "이상"
        pred  = "정상" if labels_pred[idx] == 0 else "이상"
        color = "green" if labels_true[idx] == labels_pred[idx] else "red"
        plt.subplot(3, 4, i)
        plt.imshow(img)
        plt.title(
            f"{type_labels[idx]}\nGT:{gt} / Pred:{pred}\nScore:{scores[idx]:.3f}",
            color=color, fontsize=9
        )
        plt.axis("off")
    plt.suptitle(f"초록=정답, 빨강=오답  |  Threshold={threshold:.3f}", fontsize=12)
    plt.tight_layout()
    plt.show()

show_results(test_paths, test_scores, y_true, y_pred, defect_types, threshold, n=12)

# %% [markdown]
# ## 15. OpenCV 후처리 — 이상 위치 박스 표시
#
# ### 평균 참조 이미지 + SSIM 차이 맵
# 단일 참조 이미지는 조명·각도 차이만으로도 오탐을 낼 수 있습니다.
# 정상 이미지 여러 장을 평균 내면 개별 노이즈가 상쇄됩니다.
# 참조 이미지와 테스트 이미지 양쪽에 동일하게 Blur → CLAHE 를 적용해
# 전처리 일관성을 유지합니다.

# %%
def build_mean_reference(image_paths, size=(256, 256), n_ref=30):
    """
    정상 학습 이미지를 Blur → CLAHE 순서로 전처리한 뒤 평균 내어 참조 이미지를 만듭니다.
    localize_anomaly 의 테스트 파이프라인(Blur → CLAHE)과 동일한 순서를 적용해
    SSIM 비교 기준을 일관되게 유지합니다.

    Blur → CLAHE 순서의 이유:
    CLAHE는 대비를 강화하면서 노이즈도 함께 증폭합니다.
    블러로 노이즈를 먼저 억제한 뒤 CLAHE를 적용하면 미세 노이즈 오탐을 줄입니다.
    """
    refs = []
    for p in image_paths[:n_ref]:
        img = cv2.imread(p)
        if img is None:
            continue
        img = cv2.resize(img, size)
        # Blur → CLAHE 순서 적용 (localize_anomaly 와 동일한 파이프라인)
        img = cv2.GaussianBlur(img, (3, 3), sigmaX=1)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = CLAHE.apply(lab[:, :, 0])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        refs.append(img.astype(np.float32))

    if not refs:
        raise ValueError(
            "참조 이미지를 하나도 읽을 수 없습니다. image_paths를 확인하세요."
        )
    return np.mean(refs, axis=0).astype(np.uint8)

mean_ref_bgr = build_mean_reference(train_paths, size=LOC_SIZE, n_ref=30)

plt.figure(figsize=(4, 4))
plt.imshow(cv2.cvtColor(mean_ref_bgr, cv2.COLOR_BGR2RGB))
plt.title("평균 참조 이미지 (정상 30장 평균, Blur → CLAHE 적용)")
plt.axis("off")
plt.show()

# %%
def localize_anomaly(ref_bgr, test_path, size=(256, 256), min_area=MIN_AREA):
    """
    평균 참조 이미지와 테스트 이미지를 SSIM로 비교하여
    이상 위치를 빨간 박스로 표시합니다.

    반환값
    ------
    ref_rgb   : 평균 참조 이미지 (RGB, build_mean_reference 의 CLAHE 포함)
    test_rgb  : 테스트 원본 이미지 (RGB, CLAHE 전)
    diff_map  : SSIM 이상 강도 맵 [0, 1]
    binary    : THRESH_TRIANGLE 이진화 + morphology 마스크
    boxed_rgb : 빨간 박스가 그려진 결과 이미지 (test_rgb 와 동일 기준)
    boxes     : 검출된 박스 목록 (x, y, w, h, area)
    """
    test_bgr = cv2.imread(test_path)
    if test_bgr is None:
        raise ValueError("테스트 이미지를 읽을 수 없습니다.")

    # 두 이미지를 동일한 size 로 맞춤 (shape 불일치 방지)
    ref      = cv2.resize(ref_bgr,  size)
    test_bgr = cv2.resize(test_bgr, size)

    # 시각화용 이미지 저장
    # ref_rgb  : build_mean_reference 에서 CLAHE 가 이미 적용된 상태
    # test_rgb : 이 함수 안에서 CLAHE 적용 전의 원본
    # → 두 이미지의 밝기 차이는 전처리 차이에서 비롯됨을 주의
    ref_rgb  = cv2.cvtColor(ref,      cv2.COLOR_BGR2RGB)
    test_rgb = cv2.cvtColor(test_bgr, cv2.COLOR_BGR2RGB)   # 원본 (CLAHE 전)

    # ── CLAHE 적용 (SSIM 비교용 전용) ───────────────────────────
    # ref_bgr(= mean_ref_bgr)은 build_mean_reference 에서 이미 Blur → CLAHE 가
    # 적용됐으므로 여기서 다시 적용하면 이중 적용이 됩니다.
    # ref 는 gray 변환에 바로 사용하고, test_bgr 에만 파이프라인을 적용합니다.

    # 가우시안 블러를 CLAHE 적용 전(BGR 상태)에 먼저 수행:
    # 노이즈를 억제한 뒤 대비를 강화해 엣지 오탐을 줄입니다.
    test_bgr_blurred = cv2.GaussianBlur(test_bgr, (3, 3), sigmaX=1)

    lab_test = cv2.cvtColor(test_bgr_blurred, cv2.COLOR_BGR2LAB)
    lab_test[:, :, 0] = CLAHE.apply(lab_test[:, :, 0])
    test_enhanced = cv2.cvtColor(lab_test, cv2.COLOR_LAB2BGR)

    # ref 는 이미 CLAHE 가 적용된 상태이므로 추가 CLAHE 없이 gray 변환만 수행
    ref_gray  = cv2.cvtColor(ref,          cv2.COLOR_BGR2GRAY)
    test_gray = cv2.cvtColor(test_enhanced, cv2.COLOR_BGR2GRAY)

    # SSIM 차이 맵 — 수학적 스케일링
    # SSIM 범위: [-1, 1]
    # np.clip(1 - ssim_map, 0, 1) 은 ssim < 0 구간(가장 이상한 영역)을 1로 잘라
    # 정보를 손실합니다.
    # (1 - ssim_map) / 2.0 은 [-1, 1] → [0, 1] 로 손실 없이 선형 매핑합니다.
    _, ssim_map = ssim(ref_gray, test_gray, full=True, data_range=255)
    diff_map = (1 - ssim_map) / 2.0   # [-1, 1] → [0, 1] 손실 없는 선형 매핑

    diff_8u = (diff_map * 255).astype(np.uint8)

    # ── Adaptive Threshold + Morphology ─────────────────────────
    # SSIM 차이 맵은 대부분 낮은 값에 치우친 단봉분포입니다.
    # Otsu는 이봉분포(bimodal)를 가정하므로 편향된 분포에서 경계값이 낮게 설정됩니다.
    # THRESH_TRIANGLE은 단봉 분포에서도 안정적인 경계값을 찾습니다.
    _, binary = cv2.threshold(diff_8u, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)

    kernel      = np.ones((5, 5), np.uint8)
    dil_kernel  = np.ones((3, 3), np.uint8)   # 팽창용 작은 커널 (오탐 확대 방지)
    # OPEN  : 미세 노이즈 제거
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kernel)
    # DILATE: 인접 결함 파편을 연결해 박스 검출 안정성 확보
    binary = cv2.dilate(binary, dil_kernel, iterations=1)
    # CLOSE : 팽창 후 남은 내부 공백 메우기
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # ── 윤곽선 → 바운딩 박스 ─────────────────────────────────────
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # test_bgr(원본) 기준으로 박스를 그려 test_rgb 와 시각적 기준 통일
    boxed = test_bgr.copy()
    boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        boxes.append((x, y, w, h, area))
        cv2.rectangle(boxed, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(
            boxed, f"anomaly {int(area)}",
            (x, max(y - 8, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
        )

    boxed_rgb = cv2.cvtColor(boxed, cv2.COLOR_BGR2RGB)
    return ref_rgb, test_rgb, diff_map, binary, boxed_rgb, boxes

# %% [markdown]
# ## 16. 이상 샘플에 대한 후처리 결과 확인

# %%
anomaly_candidates = [p for p, lbl in zip(test_paths, y_true) if lbl == 1]
sample_path = anomaly_candidates[0]

ref_rgb, test_rgb, diff_map, binary, boxed_rgb, boxes = localize_anomaly(
    mean_ref_bgr, sample_path, size=LOC_SIZE, min_area=MIN_AREA
)

print("검출된 박스 수:", len(boxes))
for b in boxes:
    print("박스 (x, y, w, h, area):", b)

# 탐지-시각화 불일치 확인
# IF 모델은 전역 특징으로 이상을 판정하고, SSIM 박스는 픽셀 수준 비교를 사용하므로
# 두 결과가 엇갈리는 경우(이상 판정됐으나 박스 미검출)가 발생할 수 있습니다.
sample_idx = test_paths.index(sample_path)
if y_pred[sample_idx] == 1 and len(boxes) == 0:
    print(
        f"[주의] 모델은 이상으로 판정했지만 SSIM 박스가 검출되지 않았습니다. "
        f"(Score: {test_scores[sample_idx]:.4f}, min_area={MIN_AREA} 완화 또는 "
        f"THRESH_TRIANGLE 임계값 조정을 검토하세요.)"
    )

plt.figure(figsize=(14, 10))

plt.subplot(2, 2, 1)
plt.imshow(ref_rgb)
plt.title("평균 참조 이미지 (Blur → CLAHE 적용)")
plt.axis("off")

plt.subplot(2, 2, 2)
plt.imshow(test_rgb)
plt.title("테스트 이미지 (원본)")
plt.axis("off")

plt.subplot(2, 2, 3)
plt.imshow(diff_map, cmap="hot")
plt.colorbar(fraction=0.046, pad=0.04)
plt.title("SSIM 이상 강도 맵 (밝을수록 이상)")
plt.axis("off")

plt.subplot(2, 2, 4)
plt.imshow(boxed_rgb)
plt.title("이상 위치 빨간 박스")
plt.axis("off")

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 17. 여러 이상 샘플 한눈에 확인

# %%
n_show = min(6, len(anomaly_candidates))
plt.figure(figsize=(18, 8))
for i, apath in enumerate(anomaly_candidates[:n_show]):
    _, test_rgb_i, _, _, boxed_rgb_i, boxes_i = localize_anomaly(
        mean_ref_bgr, apath, size=LOC_SIZE, min_area=MIN_AREA
    )

    # 탐지-시각화 불일치 로그
    a_idx = test_paths.index(apath)
    if y_pred[a_idx] == 1 and len(boxes_i) == 0:
        print(
            f"[주의] 이상 샘플 {i+1}: 모델 이상 판정이지만 SSIM 박스 미검출 "
            f"(Score: {test_scores[a_idx]:.4f})"
        )

    plt.subplot(2, n_show, i + 1)
    plt.imshow(test_rgb_i)
    plt.title(f"이상 샘플 {i+1}")
    plt.axis("off")

    plt.subplot(2, n_show, n_show + i + 1)
    plt.imshow(boxed_rgb_i)
    plt.title("탐지 결과")
    plt.axis("off")

plt.suptitle("상단: 원본  |  하단: 탐지 결과", fontsize=13)
plt.tight_layout()
plt.show()
