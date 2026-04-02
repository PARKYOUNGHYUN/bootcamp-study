FEATURES = [
    'Air temperature [K]', 'Process temperature [K]', 'Temp_Diff',
    'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
    'Type_L', 'Type_M', 'Type_H',
]
INPUT_SIZE = len(FEATURES)
SEQUENCE_LENGTH = 10
TRAIN_RATIO = 0.8
BATCH_SIZE = 32
LR = 0.001
EXCLUDE_FAILURE_TYPES = ['No Failure', 'Random Failures']

# Baseline (main_1 approach): 전체 정상 데이터 학습
BASELINE_HIDDEN_SIZE = 20
BASELINE_EPOCHS = 15

# Improved (copy4 approach): 시간순 분리 + 순수 정상 필터링
IMPROVED_HIDDEN_SIZE = 8
IMPROVED_EPOCHS = 50

# 노트북 기준 상대 경로
DATA_PATH = '../data/predictive_maintenance.csv'
CHECKPOINT_DIR = '../checkpoints'
OUTPUT_DIR = '../outputs'
