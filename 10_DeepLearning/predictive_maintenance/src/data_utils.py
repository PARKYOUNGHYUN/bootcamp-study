import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_and_engineer(csv_path):
    """CSV 로드 후 Temp_Diff 피처 추가 및 Type 원-핫 인코딩."""
    df = pd.read_csv(csv_path)
    df['Temp_Diff'] = df['Process temperature [K]'] - df['Air temperature [K]']
    type_dummies = pd.get_dummies(df['Type'], prefix='Type')
    return pd.concat([df, type_dummies], axis=1)


def create_windows(data, window_size):
    """오토인코더용 슬라이딩 윈도우 (X = y)."""
    X = [data[i:i + window_size] for i in range(len(data) - window_size + 1)]
    X = np.array(X)
    return X, X


def prepare_autoencoder_data(scaled_data, target_values, window_size, is_train=True):
    """슬라이딩 윈도우 생성.

    is_train=True: 윈도우 내 고장이 하나도 없는 순수 정상 시퀀스만 추출.
    is_train=False: 모든 시퀀스 추출 (정상 + 고장 혼합).
    """
    X, y = [], []
    for i in range(len(scaled_data) - window_size + 1):
        window = scaled_data[i:i + window_size]
        if is_train and np.sum(target_values[i:i + window_size]) > 0:
            continue
        X.append(window)
        y.append(window)
    return np.array(X), np.array(y)


def prepare_classifier_data_simple(failure_scaled, failure_labels, window_size):
    """Baseline용: 고장 데이터만 미리 추출한 뒤 슬라이딩 윈도우 생성."""
    X, y = [], []
    for i in range(len(failure_scaled) - window_size + 1):
        X.append(failure_scaled[i:i + window_size])
        y.append(failure_labels[i + window_size - 1])
    return np.array(X), np.array(y)


def prepare_classifier_data(all_scaled, all_labels, window_size, exclude_types):
    """Improved용: 전체 데이터에 슬라이딩 윈도우 후 특정 고장 유형만 필터링.

    exclude_types에 해당하는 라벨('No Failure', 'Random Failures' 등)을 제외하고
    남은 고장 유형만 분류 대상으로 반환한다.
    """
    X_all, y_all = [], []
    for i in range(len(all_scaled) - window_size + 1):
        X_all.append(all_scaled[i:i + window_size])
        y_all.append(all_labels[i + window_size - 1])
    X_all, y_all = np.array(X_all), np.array(y_all)

    mask = ~np.isin(y_all, exclude_types)
    X_fail = X_all[mask]
    y_fail_raw = y_all[mask]

    le = LabelEncoder()
    y_fail = le.fit_transform(y_fail_raw)
    return X_fail, y_fail, le
