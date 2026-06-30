import torch.nn as nn


class LSTMAutoencoder(nn.Module):
    """시계열 이상 탐지용 LSTM 오토인코더.

    정상 패턴을 학습하고, 재구성 오차로 이상 여부를 판정한다.
    """
    def __init__(self, input_size, hidden_size, sequence_length):
        super().__init__()
        self.hidden_size = hidden_size
        self.sequence_length = sequence_length
        self.encoder = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                               num_layers=1, batch_first=True)
        # 디코더: hidden_size → input_size (원래 특성 크기로 복원)
        self.decoder = nn.LSTM(input_size=hidden_size, hidden_size=input_size,
                               num_layers=1, batch_first=True)
        self.fc = nn.Linear(input_size, input_size)

    def forward(self, x):
        _, (hidden, _) = self.encoder(x)
        decoder_input = hidden.permute(1, 0, 2).repeat(1, self.sequence_length, 1)
        output, _ = self.decoder(decoder_input)
        return self.fc(output)


class LSTMClassifier(nn.Module):
    """고장 유형 다중 분류용 LSTM 분류기."""
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        _, (hidden, _) = self.lstm(x)
        return self.fc(hidden[-1])
