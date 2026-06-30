import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        loss = criterion(model(inputs), targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            total_loss += criterion(model(inputs), targets).item()
    return total_loss / len(loader)


def compute_errors(model, loader, device):
    """배치별 샘플당 MSE를 계산하여 1D 배열로 반환."""
    model.eval()
    errors = []
    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = torch.mean((outputs - targets) ** 2, dim=(1, 2))
            errors.extend(loss.cpu().numpy())
    return np.array(errors)


def train_autoencoder(model, train_loader, val_loader, num_epochs, lr, device, save_path):
    """오토인코더 학습 루프. 최저 val_loss 모델을 save_path에 저장한다."""
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    history = {'train_loss': [], 'val_loss': []}
    best_val_loss = float('inf')

    print(f'학습 시작 | {num_epochs} 에포크')
    print('=' * 60)
    print(f"{'에포크':^6} | {'훈련 Loss':^12} | {'검증 Loss':^12}")
    print('-' * 60)

    for epoch in range(1, num_epochs + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), save_path)
            mark = ' ⭐'
        else:
            mark = ''
        print(f"  {epoch:^4}   | {train_loss:^10.4f} | {val_loss:^10.4f}{mark}")

    return history
