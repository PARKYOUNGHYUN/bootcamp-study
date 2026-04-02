import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False


def plot_loss_curve(history, save_path=None):
    plt.figure(figsize=(10, 6))
    plt.plot(history['train_loss'], label='Train Loss', color='#1f77b4', linewidth=2)
    plt.plot(history['val_loss'], label='Val Loss', color='#ff7f0e', linewidth=2, linestyle='--')
    plt.title('학습 손실 곡선', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def plot_error_distribution(train_errors, test_errors, y_true, threshold, save_path=None):
    plt.figure(figsize=(10, 5))
    plt.hist(train_errors, bins=100, alpha=0.6, label='정상 (훈련)')
    plt.hist(test_errors[y_true == 1], bins=100, alpha=0.6, label='고장 (테스트)')
    plt.axvline(threshold, color='black', linestyle='--', label=f'Threshold ({threshold:.4f})')
    plt.title('정상 vs 고장 오차 분포')
    plt.xlabel('재구성 오차 (MSE)')
    plt.ylabel('빈도')
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def plot_error_timeseries(test_errors, y_true, threshold, save_path=None):
    plt.figure(figsize=(15, 5))
    plt.plot(test_errors, label='재구성 오차', color='blue', alpha=0.6)
    plt.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold ({threshold:.4f})')
    for idx in np.where(y_true == 1)[0]:
        plt.axvline(x=idx, color='orange', alpha=0.2)
    plt.title('재구성 오차 추이와 실제 고장 구간')
    plt.xlabel('시간 (인덱스)')
    plt.ylabel('재구성 오차')
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def plot_confusion_matrix(y_true, y_pred, labels, title, save_path=None):
    plt.figure(figsize=(6, 5))
    sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d', cmap='Oranges',
                xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.xticks(rotation=15)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()
