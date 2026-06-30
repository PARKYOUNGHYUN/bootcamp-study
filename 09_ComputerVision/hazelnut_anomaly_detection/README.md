# hazelnut_anomaly_detection

MVTec AD `hazelnut` 데이터셋을 이용해 **정상 이미지만으로 학습**한 뒤,
테스트 이미지의 정상/이상을 판별하고 이상 위치를 시각화하는 프로젝트입니다.

---

## 데이터셋

- **MVTec Anomaly Detection (MVTec AD)** — `hazelnut` 카테고리
- 학습: 정상(good) 이미지 391장
- 테스트: 정상 40장 + 이상 70장 (총 110장)
- 이상 유형: crack / cut / hole / print

데이터는 `./data/hazelnut/` 에 직접 배치해야 합니다.  
공식 다운로드: <https://www.mvtec.com/company/research/datasets/mvtec-ad>

---

## 폴더 구조

```
hazelnut_anomaly_detection/
├── solution.py              # 최종 제출 코드 (멀티스케일 LBP + IF 앙상블)
├── README.md
├── data/
│   └── hazelnut/
│       ├── train/good/
│       ├── test/            # crack / cut / hole / print / good
│       └── ground_truth/    # crack / cut / hole / print (픽셀 단위 정답 마스크)
├── experiments/
│   ├── solution_aug.py      # 회전 증강 포함 확장 버전
│   └── team_variants/       # 팀원 개인 실험 버전
│       ├── hyuna.py
│       └── yugyong.py
└── visualizations/          # 발표용 시각화 스크립트 및 출력 이미지
```

---

## 주요 파일 설명

### `solution.py` — 최종 제출 코드

베이스라인 대비 개선된 핵심 내용:

| 항목 | 베이스라인 | 최종 |
|------|-----------|------|
| 이미지 크기 | 128×128 | 256×256 |
| 이미지 전처리 | Blur → CLAHE | 원본 Grayscale (미세 결함 패턴 보존) |
| LBP 추출 | 전역 단일 스케일 | 4×4 Grid × 반지름 [1,2,3] 멀티스케일 |
| 정규화 | StandardScaler | 제거 (LBP는 이미 확률 분포) |
| 모델 | 단일 IsolationForest | 앙상블 3개 (random_state 평균) |
| Threshold | train 하위 5%ile | validation 65%ile (정보 누수 없음) |
| 이상 위치 이진화 | Otsu | THRESH_TRIANGLE |
| Morphology | OPEN → CLOSE | OPEN → DILATE → CLOSE |

### `experiments/`

- `solution_aug.py` — solution.py에 30° 간격 회전 증강(11개 각도)과 오탐(FP) 분석 섹션을 추가한 확장 버전
- `team_variants/` — 팀원별 실험 파라미터 변형 버전
  - `hyuna.py`: 단일 모델(random_state=42), 864차원 특징, Anomaly F1=0.7630
  - `yugyong.py`: 최종 앙상블과 동일한 파라미터

### `visualizations/` — 발표용 시각화

| 파일 | 내용 |
|------|------|
| `lbp_overview.py` | LBP 인코딩 원리, Grid 분할, 멀티스케일 비교, 성능 개선 단계 |
| `lbp_encoding_detail.py` | LBP 인코딩 4단계 상세 다이어그램 |
| `grid_lbp_comparison.py` | 전역 LBP vs Grid 4×4 LBP 히스토그램 비교 |
| `confusion_matrix.py` | 혼동 행렬 히트맵 |
| `threshold_analysis.py` | Threshold 퍼센타일 실험 결과 막대 그래프 |

출력 이미지 (`.png`): `lbp_concept`, `lbp_encoding_process`, `global_vs_grid`, `improvement`, `confusion_matrix_*`, `threshold_experiment_*`

---

## 실행 방법

### 환경 설정

```bash
pip install scikit-image scikit-learn opencv-python matplotlib koreanize-matplotlib
```

### 최종 코드 실행

```bash
python solution.py
```

또는 VS Code / Jupyter에서 `# %%` 셀 단위로 실행할 수 있습니다.

---

## 성능 결과

`solution.py` 기준 (MVTec AD hazelnut 테스트셋):

| 지표 | 값 |
|------|----|
| Anomaly F1-score | **0.7647** |
| Anomaly Recall | **0.93** |
| Normal Recall | 0.12 |
| ROC AUC (참고) | 0.5725 |

> ROC AUC가 낮은 이유: IsolationForest의 `decision_function` 점수 분포가
> 정상/이상 클래스 간 중첩이 커서 순위 기반 지표가 낮게 나옵니다.
> Threshold 65%ile 설정으로 Recall을 우선시한 결과, 정상 오탐(FP)이 증가합니다.

---

## 핵심 알고리즘 요약

### 멀티스케일 LBP + 4×4 Grid

```
특징 벡터 차원 = 16 셀 × (10 + 18 + 26) bins = 864차원
  - 반지름 1 (n_points=8):  bins=10
  - 반지름 2 (n_points=16): bins=18
  - 반지름 3 (n_points=24): bins=26
```

### IsolationForest 앙상블

```python
RANDOM_STATES = [42, 123, 7]
n_estimators  = 500
max_samples   = 0.8
max_features  = 1.0
contamination = 'auto'
```

앙상블 점수 = 3개 모델 `decision_function` 평균

### Threshold

```python
threshold = np.percentile(val_scores, 65)
# validation = train 데이터 80/20 분리 후 20% 사용 (테스트 레이블 미사용)
```

### 이상 위치 검출 파이프라인

```
평균 참조 이미지 (정상 30장, Blur → CLAHE)
  → SSIM 비교 → diff_map
  → THRESH_TRIANGLE 이진화
  → OPEN → DILATE → CLOSE
  → 윤곽선 → 바운딩 박스
```

---

## 라이브러리

| 라이브러리 | 용도 |
|-----------|------|
| `scikit-image` | LBP 특징 추출, SSIM |
| `scikit-learn` | IsolationForest, 평가 지표 |
| `opencv-python` | 이미지 처리, CLAHE, Morphology |
| `numpy` | 수치 계산 |
| `matplotlib` | 결과 시각화 |
| `koreanize-matplotlib` | 한글 폰트 지원 |
