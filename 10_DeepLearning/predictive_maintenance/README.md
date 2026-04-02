# 설비 고장 유형 예측 (predictive_maintenance)

LSTM 오토인코더를 활용한 산업 설비 이상 탐지 및 고장 유형 분류 프로젝트

---

## 개요

정상 설비 데이터의 패턴을 학습한 뒤, 재구성 오차(Reconstruction Error)를 기준으로 이상을 감지하고 고장 유형을 분류하는 **2단계 파이프라인**을 구현합니다.

- **Stage 1**: LSTM Autoencoder로 이상 탐지 (정상 / 이상 이진 분류)
- **Stage 2**: LSTM Classifier로 고장 유형 다중 분류

---

## 디렉토리 구조

```
.
├── notebooks/
│   ├── 01_baseline.ipynb     # Stage 1·2 기본 구현 (전체 정상 데이터 학습)
│   └── 02_improved.ipynb     # Stage 1·2 개선 구현 (시간순 분리 + 순수 정상 필터링)
├── src/
│   ├── config.py             # 하이퍼파라미터 및 경로 설정
│   ├── models.py             # LSTMAutoencoder, LSTMClassifier 클래스
│   ├── data_utils.py         # 데이터 로드, 피처 엔지니어링, 슬라이딩 윈도우
│   ├── train_utils.py        # 학습 루프, 오차 계산 함수
│   └── visualization.py      # 시각화 함수 모음
├── checkpoints/
│   └── autoencoder_v2.pth    # 02_improved 학습 결과 모델 가중치
├── outputs/
│   ├── confusion_matrix_stage1.png
│   ├── confusion_matrix_stage2.png
│   ├── error_timeseries.png
│   └── failure_counts.png
└── data/
    └── predictive_maintenance.csv
```

---

## 데이터셋

| 항목 | 내용 |
|---|---|
| 샘플 수 | 10,000개 |
| 정상 / 고장 비율 | 96.5% / 3.5% |
| 입력 피처 | 9개 (온도, 회전수, 토크, 공구마모, 설비 타입 등) |
| 고장 유형 | Heat Dissipation, Overstrain, Power, Tool Wear Failure |

**사용 피처**

```python
['Air temperature [K]', 'Process temperature [K]', 'Temp_Diff',
 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
 'Type_L', 'Type_M', 'Type_H']
```

> `Temp_Diff` = 공정 온도 − 기온 (열 발생 정도를 나타내는 파생 피처)

---

## 모델 구조

### Stage 1 — LSTM Autoencoder (이상 탐지)

```
입력 시퀀스 (seq_len=10, features=9)
    → Encoder LSTM → 잠재 벡터 (hidden_size)
    → Decoder LSTM → 복원 시퀀스
    → FC Layer → 최종 복원값

재구성 오차(MSE) > Threshold → 이상 판정
```

### Stage 2 — LSTM Classifier (고장 유형 분류)

```
이상 탐지된 시퀀스
    → LSTM → hidden state
    → FC Layer → 4개 고장 유형 분류
```

---

## 노트북 비교

| | 01_baseline | 02_improved |
|---|---|---|
| 오토인코더 학습 데이터 | 정상 행 전체 | 시간순 80% 구간 내 순수 정상 시퀀스 |
| HIDDEN_SIZE | 20 | 8 |
| 학습 에포크 | 15 | 50 |
| 테스트 셋 | 전체 데이터 (~9,991) | 시간순 후반 20% (~1,991) |
| 고장 분류 대상 | 전체 고장 유형 | No Failure·Random Failures 제외 4종 |
| 시각화 | 혼동 행렬 | 손실 곡선, 오차 분포, 시계열, 혼동 행렬 |

---

## 실행 방법

```bash
# notebooks/ 디렉토리에서 Jupyter 실행
jupyter notebook
```

노트북 내부에서 `src/` 모듈을 `..`(부모 디렉토리) 기준으로 import합니다.  
반드시 `notebooks/` 폴더 내에서 커널을 실행하세요.

---

## 요구 사항

```
torch
numpy
pandas
scikit-learn
matplotlib
seaborn
```
