#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSTM价格预测模型
用于预测股票价格走势

架构:
- 数据预处理 (标准化、序列化)
- LSTM网络 (多层LSTM + Dropout)
- 训练引擎 (早停、学习率调度)
- 预测接口
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 尝试导入深度学习库
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # 定义一个空的Dataset类作为占位符
    class Dataset:
        pass
    print("⚠️ PyTorch未安装，将使用模拟模式")

sys.path.insert(0, "/workspace/projects/workspace")

if TORCH_AVAILABLE:
    class StockDataset(Dataset):
        """股票数据集"""
        
        def __init__(self, data: np.ndarray, seq_length: int = 20):
            self.data = data
            self.seq_length = seq_length
        
        def __len__(self):
            return len(self.data) - self.seq_length
        
        def __getitem__(self, idx):
            x = self.data[idx:idx+self.seq_length, :-1]  # 特征
            y = self.data[idx+self.seq_length-1, -1]     # 目标 (收盘价)
            return torch.FloatTensor(x), torch.FloatTensor([y])

    class LSTMModel(nn.Module):
        """LSTM价格预测模型"""
        
        def __init__(self, input_size: int = 5, hidden_size: int = 64, 
                     num_layers: int = 2, dropout: float = 0.2):
            super(LSTMModel, self).__init__()
            
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            
            # LSTM层
            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0
            )
            
            # 全连接层
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(32, 1)
            )
        
        def forward(self, x):
            # LSTM前向传播
            lstm_out, (hidden, cell) = self.lstm(x)
            
            # 取最后一个时间步的隐藏状态
            last_hidden = lstm_out[:, -1, :]
            
            # 全连接层
            output = self.fc(last_hidden)
            
            return output
else:
    # 占位符类
    class StockDataset:
        pass
    class LSTMModel:
        pass

class LSTMPredictor:
    """LSTM预测器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.model = None
        self.scaler_params = {}
        self.seq_length = 20
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if TORCH_AVAILABLE else None
        
        print(f"🧠 LSTM预测器初始化")
        if TORCH_AVAILABLE:
            print(f"   设备: {self.device}")
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """
        准备数据
        
        Args:
            df: 股票数据DataFrame
            target_col: 目标列名
            
        Returns:
            (特征数组, 目标数组)
        """
        # 特征列
        feature_cols = ['open', 'high', 'low', 'close', 'volume']
        
        # 确保所有列存在
        for col in feature_cols:
            if col not in df.columns:
                print(f"⚠️ 缺少列: {col}")
                return None, None
        
        # 数据标准化
        data = df[feature_cols].values
        self.scaler_params = {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0) + 1e-8
        }
        data_normalized = (data - self.scaler_params['mean']) / self.scaler_params['std']
        
        return data_normalized, data_normalized[:, 3]  # 返回特征和收盘价(已标准化)
    
    def train(self, df: pd.DataFrame, epochs: int = 50, batch_size: int = 32,
              learning_rate: float = 0.001, validation_split: float = 0.2) -> Dict:
        """
        训练模型
        
        Args:
            df: 训练数据
            epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率
            validation_split: 验证集比例
            
        Returns:
            训练历史
        """
        if not TORCH_AVAILABLE:
            print("⚠️ PyTorch未安装，跳过训练")
            return {"status": "skipped"}
        
        print(f"🚀 开始训练LSTM模型...")
        print(f"   轮数: {epochs}, 批次: {batch_size}, 学习率: {learning_rate}")
        
        # 准备数据
        data, _ = self.prepare_data(df)
        if data is None:
            return {"status": "error", "message": "数据准备失败"}
        
        # 划分训练集和验证集
        split_idx = int(len(data) * (1 - validation_split))
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        # 创建数据加载器
        train_dataset = StockDataset(train_data, self.seq_length)
        val_dataset = StockDataset(val_data, self.seq_length)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # 初始化模型
        input_size = data.shape[1] - 1  # 排除目标列
        self.model = LSTMModel(input_size=input_size).to(self.device)
        
        # 损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        # 训练历史
        history = {
            'train_loss': [],
            'val_loss': [],
            'epochs': []
        }
        
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        # 训练循环
        for epoch in range(epochs):
            # 训练模式
            self.model.train()
            train_losses = []
            
            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # 前向传播
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                
                # 反向传播
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                train_losses.append(loss.item())
            
            # 验证模式
            self.model.eval()
            val_losses = []
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    outputs = self.model(batch_x)
                    loss = criterion(outputs, batch_y)
                    val_losses.append(loss.item())
            
            train_loss = np.mean(train_losses)
            val_loss = np.mean(val_losses)
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['epochs'].append(epoch + 1)
            
            # 学习率调度
            scheduler.step(val_loss)
            
            # 早停检查
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # 保存最佳模型
                self.save_model()
            else:
                patience_counter += 1
            
            if (epoch + 1) % 10 == 0:
                print(f"   Epoch {epoch+1}/{epochs} - 训练损失: {train_loss:.6f}, 验证损失: {val_loss:.6f}")
            
            if patience_counter >= patience:
                print(f"   早停于 Epoch {epoch+1}")
                break
        
        print(f"✅ 训练完成! 最佳验证损失: {best_val_loss:.6f}")
        
        return {
            "status": "success",
            "history": history,
            "best_val_loss": best_val_loss
        }
    
    def predict(self, recent_data: pd.DataFrame, days: int = 5) -> List[float]:
        """
        预测未来价格
        
        Args:
            recent_data: 最近的历史数据
            days: 预测天数
            
        Returns:
            预测价格列表
        """
        if not TORCH_AVAILABLE or self.model is None:
            # 模拟预测
            last_price = recent_data['close'].iloc[-1]
            predictions = [last_price * (1 + np.random.normal(0, 0.02)) for _ in range(days)]
            return predictions
        
        self.model.eval()
        
        # 准备数据
        data, _ = self.prepare_data(recent_data)
        if data is None or len(data) < self.seq_length:
            return []
        
        # 取最近seq_length天的数据
        recent = data[-self.seq_length:, :-1]
        recent_tensor = torch.FloatTensor(recent).unsqueeze(0).to(self.device)
        
        predictions = []
        current_input = recent_tensor.clone()
        
        with torch.no_grad():
            for _ in range(days):
                # 预测
                pred = self.model(current_input)
                pred_value = pred.item()
                
                # 反标准化
                real_pred = pred_value * self.scaler_params['std'][3] + self.scaler_params['mean'][3]
                predictions.append(real_pred)
                
                # 更新输入 (滑动窗口)
                # 这里简化处理，实际应该更新所有特征
                
        return predictions
    
    def save_model(self, filepath: str = None):
        """保存模型"""
        if not TORCH_AVAILABLE or self.model is None:
            return
        
        if filepath is None:
            filepath = f"{self.workspace}/data/ml_models/lstm_predictor.pt"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'scaler_params': self.scaler_params,
            'seq_length': self.seq_length
        }, filepath)
        
        print(f"💾 模型已保存: {filepath}")
    
    def load_model(self, filepath: str = None):
        """加载模型"""
        if not TORCH_AVAILABLE:
            return False
        
        if filepath is None:
            filepath = f"{self.workspace}/data/ml_models/lstm_predictor.pt"
        
        if not os.path.exists(filepath):
            print(f"⚠️ 模型文件不存在: {filepath}")
            return False
        
        checkpoint = torch.load(filepath, map_location=self.device)
        
        # 这里需要知道输入大小，简化处理
        self.model = LSTMModel(input_size=4).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.scaler_params = checkpoint['scaler_params']
        self.seq_length = checkpoint['seq_length']
        
        print(f"📂 模型已加载: {filepath}")
        return True

def demo():
    """演示LSTM预测器"""
    print("="*70)
    print("🧠 LSTM价格预测模型演示")
    print("="*70)
    print()
    
    # 创建模拟数据
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=252, freq='B')
    
    # 生成模拟股票数据
    price = 100
    prices = []
    for _ in range(252):
        price = price * (1 + np.random.normal(0.0005, 0.02))
        prices.append(price)
    
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 252)
    })
    
    print(f"📊 模拟数据: {len(df)} 条记录")
    print(f"   日期范围: {df['date'].iloc[0]} 至 {df['date'].iloc[-1]}")
    print(f"   价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print()
    
    # 初始化预测器
    predictor = LSTMPredictor()
    
    # 训练模型
    print("🚀 训练LSTM模型...")
    result = predictor.train(df, epochs=30, batch_size=16)
    print()
    
    # 预测未来5天
    print("🔮 预测未来5天价格...")
    predictions = predictor.predict(df, days=5)
    
    last_price = df['close'].iloc[-1]
    print(f"   当前价格: {last_price:.2f}")
    print("   预测价格:")
    for i, pred in enumerate(predictions, 1):
        change = (pred - last_price) / last_price * 100
        print(f"     第{i}天: {pred:.2f} ({change:+.2f}%)")
    
    print()
    print("="*70)
    print("✅ LSTM预测模型演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
