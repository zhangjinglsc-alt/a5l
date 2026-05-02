# A5L Phase 2: 功能归类与接口统一报告

## 📊 按投资流程重组的功能分类

### 发现 (Discovery)
发现投资机会，扫描市场

**包含SKILL**:
- `layer1_alternative_data`
- `layer1_data_lineage`
- `layer2_macro_timing_model`
- `layer3_industry_chain`
- `layer4_dynamic_rebalance`

### 分析 (Analysis)
深度分析标的，评估价值与风险

**包含SKILL**:
- `layer1_data_quality_monitor`
- `layer1_data_access_control`
- `layer1_data_compliance`
- `layer2_strategy_performance`
- `layer2_longterm_backtest`
- `layer3_reasoning_chain`
- `layer3_result_validation`
- `layer3_bias_detector`
- `layer3_compound_analysis`
- `layer4_consistency_check`

### 决策 (Decision)
做出投资决策，确定仓位

**包含SKILL**:
- `layer2_strategy_version_manager`
- `layer2_strategy_ethics`
- `layer3_anomaly_alert`
- `layer4_decision_audit_log`
- `layer4_risk_circuit_breaker`
- `layer4_trade_interceptor`
- `layer4_position_manager`

### 执行 (Execution)
执行交易，管理订单

**包含SKILL**:
- `layer1_data_auto_repair`
- `layer2_strategy_sandbox`
- `layer2_strategy_recovery`
- `layer3_task_queue`
- `layer4_execution_optimizer`
- `layer4_dynamic_rebalance`

### 复盘 (Review)
复盘总结，持续改进

**包含SKILL**:
- `layer1_data_archival`
- `layer5_review_workflow`
- `layer5_attribution_analysis`
- `layer5_architecture_evolution`
- `layer5_investment_capability`
- `layer5_anomaly_behavior`
- `layer5_improvement_eval`
- `layer5_learning_anomaly`
- `layer5_knowledge_compound`

### 基础设施 (Infrastructure)
系统基础设施，支撑全链路

**包含SKILL**:
- `integration_engine`
- `user_habits_learning`
- `layer1_data_quality_monitor`
- `layer2_strategy_performance`
- `layer3_task_queue`

## 🔧 统一接口规范

### 分析器接口 (BaseAnalyzer)
```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, symbol: str, context: Dict) -> AnalysisReport: pass

    @abstractmethod
    def validate_inputs(self, symbol: str, context: Dict) -> bool: pass
```

### 策略接口 (BaseStrategy)
```python
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, symbol: str, context: Dict) -> TradingSignal: pass

    @abstractmethod
    def backtest(self, symbol: str, start: str, end: str) -> Dict: pass
```

### 数据源接口 (BaseDataSource)
```python
class BaseDataSource(ABC):
    @abstractmethod
    def fetch(self, symbol: str, data_type: str, params: Dict) -> Dict: pass

    @abstractmethod
    def check_health(self) -> Dict: pass
```

### 执行器接口 (BaseExecutor)
```python
class BaseExecutor(ABC):
    @abstractmethod
    def execute(self, signal: TradingSignal, context: Dict) -> Dict: pass

    @abstractmethod
    def validate_risk(self, signal: TradingSignal) -> bool: pass
```

### 学习模块接口 (BaseLearningModule)
```python
class BaseLearningModule(ABC):
    @abstractmethod
    def review(self, period: str, data: Dict) -> Dict: pass

    @abstractmethod
    def improve(self, findings: Dict) -> bool: pass
```

## 🎯 统一API入口

```python
from a5l_unified_api import A5LUnifiedAPI

a5l = A5LUnifiedAPI()

# 完整投资流程
result = a5l.investment_pipeline(
    symbol="600519.SH",
    steps=["discover", "analyze", "decide", "execute", "review"]
)
```