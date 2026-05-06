# Layer 6 ML技能文档

**Layer**: 6 (机器学习)  
**创建时间**: 2026-05-02  
**状态**: ✅ 已部署

## 组件列表

### 1. LSTM价格预测 (lstm_predictor.py)
- 功能: 股票价格预测
- 架构: 多层LSTM + Dropout
- 输入: OHLCV 5维特征
- 输出: 未来N天价格
- 训练: 早停 + 学习率调度

### 2. XGBoost分类 (xgboost_classifier.py)
- 功能: 涨跌方向分类
- 特征: 29个技术指标
- 评估: 准确率/精确率/召回率/F1/AUC
- 输出: 涨跌方向 + 置信度

### 3. ML Pipeline (ml_pipeline.py)
- 功能: 统一训练/预测接口
- 集成: LSTM + XGBoost投票
- 回测: 模型性能验证
- 报告: 自动生成

### 4. 推送系统 (push_notification_system.py)
- WebSocket: ws://localhost:8765
- 飞书: Webhook集成
- 通知: 价格异动/交易信号/系统告警

### 5. A/B测试 (ab_test_framework.py)
- 测试: 多策略变体对比
- 分析: 绩效指标 + 统计检验
- 选择: 自动最优策略推荐

### 6. 多因子模型 (multi_factor_model.py)
- 因子: Barra 20+风格因子
- 检验: IC/IR/T检验
- 组合: 3种加权方法
- 输出: 综合因子得分

## 使用示例



## 依赖
- PyTorch (LSTM)
- XGBoost (分类)
- scikit-learn (评估)
- websockets (推送)
