#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 SKILL批量开发 - L0角色提出的最高优先级需求
立即开发所有P0技能！
"""

import os

# 创建所有P0技能文件的脚本

SKILLS_TO_CREATE = {
    # L1 - 数据层
    "layer1_data_quality_monitor.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L1 P0: 数据质量监控系统
提出者: Chief Operating Officer (牛逼组织者)
\"\"\"
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityMonitor:
    \"\"\"数据质量监控 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.quality_metrics = {}
        logger.info("📊 Data Quality Monitor initialized")
    
    def check_data_source_health(self, source_name: str) -> Dict:
        \"\"\"检查数据源健康度\"\"\"
        checks = {
            'availability': self._check_availability(source_name),
            'latency': self._check_latency(source_name),
            'accuracy': self._check_accuracy(source_name),
            'completeness': self._check_completeness(source_name),
            'freshness': self._check_freshness(source_name)
        }
        
        overall_score = sum(checks.values()) / len(checks)
        
        return {
            'source': source_name,
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'checks': checks,
            'status': 'healthy' if overall_score > 0.8 else 'degraded' if overall_score > 0.5 else 'critical'
        }
    
    def _check_availability(self, source: str) -> float:
        \"\"\"检查可用性\"\"\"
        return 0.95  # 模拟95%可用
    
    def _check_latency(self, source: str) -> float:
        \"\"\"检查延迟\"\"\"
        return 0.90  # 模拟延迟良好
    
    def _check_accuracy(self, source: str) -> float:
        \"\"\"检查准确性\"\"\"
        return 0.92  # 模拟准确性良好
    
    def _check_completeness(self, source: str) -> float:
        \"\"\"检查完整性\"\"\"
        return 0.88  # 模拟完整性良好
    
    def _check_freshness(self, source: str) -> float:
        \"\"\"检查时效性\"\"\"
        return 0.93  # 模拟时效性良好
""",

    "layer1_data_access_control.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L1 P0: 数据访问控制系统
提出者: Chief Security Officer (安全师)
\"\"\"
import logging
from typing import Dict, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataAccessControl:
    \"\"\"数据访问控制 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.permissions = {}
        self.access_log = []
        logger.info("🔒 Data Access Control initialized")
    
    def check_permission(self, user_id: str, data_path: str, 
                        action: str = "read") -> bool:
        \"\"\"检查权限\"\"\"
        # 模拟权限检查
        allowed = True  # 实际应查询权限表
        
        self._log_access(user_id, data_path, action, allowed)
        
        return allowed
    
    def _log_access(self, user_id: str, data_path: str, 
                   action: str, allowed: bool):
        \"\"\"记录访问日志\"\"\"
        from datetime import datetime
        self.access_log.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_id,
            'data': data_path,
            'action': action,
            'allowed': allowed
        })
""",

    # L2 - 策略层
    "layer2_strategy_version_manager.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L2 P0: 策略版本管理系统
提出者: Chief Architect (顶级架构师)
\"\"\"
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StrategyVersion:
    version: str
    timestamp: str
    changes: List[str]
    author: str
    backtest_results: Dict
    performance_metrics: Dict

class StrategyVersionManager:
    \"\"\"策略版本管理 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.versions = {}
        logger.info("📦 Strategy Version Manager initialized")
    
    def create_version(self, strategy_id: str, changes: List[str],
                      author: str, backtest: Dict) -> StrategyVersion:
        \"\"\"创建新版本\"\"\"
        version_id = f"v{len(self.versions.get(strategy_id, [])) + 1}.0"
        
        version = StrategyVersion(
            version=version_id,
            timestamp=datetime.now().isoformat(),
            changes=changes,
            author=author,
            backtest_results=backtest,
            performance_metrics=backtest.get('metrics', {})
        )
        
        if strategy_id not in self.versions:
            self.versions[strategy_id] = []
        
        self.versions[strategy_id].append(version)
        
        logger.info(f"✅ Created version {version_id} for {strategy_id}")
        return version
    
    def get_version_history(self, strategy_id: str) -> List[StrategyVersion]:
        \"\"\"获取版本历史\"\"\"
        return self.versions.get(strategy_id, [])
    
    def rollback_to_version(self, strategy_id: str, 
                           version_id: str) -> bool:
        \"\"\"回滚到指定版本\"\"\"
        logger.info(f"🔄 Rolling back {strategy_id} to {version_id}")
        return True
""",

    "layer2_macro_timing_model.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L2 P0: 宏观择时模型
提出者: Chief Investment Officer (顶级投资人)
\"\"\"
import logging
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketCycle(Enum):
    RECOVERY = "复苏期"
    EXPANSION = "扩张期"
    SLOWDOWN = "放缓期"
    CONTRACTION = "收缩期"

class MacroTimingModel:
    \"\"\"宏观择时模型 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.economic_indicators = {}
        self.market_signals = {}
        logger.info("🌐 Macro Timing Model initialized")
    
    def analyze_economic_cycle(self, data: Dict) -> Dict:
        \"\"\"分析经济周期\"\"\"
        # GDP增长
        gdp_growth = data.get('gdp_growth', 0.05)
        # 通胀率
        inflation = data.get('inflation', 0.02)
        # 利率
        interest_rate = data.get('interest_rate', 0.03)
        # 失业率
        unemployment = data.get('unemployment', 0.05)
        
        # 判断周期
        if gdp_growth > 0.03 and inflation < 0.03:
            cycle = MarketCycle.RECOVERY
            allocation = {"stocks": 0.70, "bonds": 0.20, "cash": 0.10}
        elif gdp_growth > 0.05:
            cycle = MarketCycle.EXPANSION
            allocation = {"stocks": 0.80, "bonds": 0.15, "cash": 0.05}
        elif gdp_growth > 0:
            cycle = MarketCycle.SLOWDOWN
            allocation = {"stocks": 0.50, "bonds": 0.40, "cash": 0.10}
        else:
            cycle = MarketCycle.CONTRACTION
            allocation = {"stocks": 0.30, "bonds": 0.50, "cash": 0.20}
        
        return {
            'cycle': cycle.value,
            'confidence': 0.75,
            'allocation': allocation,
            'signals': {
                'gdp': gdp_growth,
                'inflation': inflation,
                'interest_rate': interest_rate,
                'unemployment': unemployment
            }
        }
""",

    # L3 - 分析层
    "layer3_reasoning_chain.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L3 P0: 分析推理链系统
提出者: Chief Architect (顶级架构师)
\"\"\"
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    step_id: str
    description: str
    input_data: Dict
    reasoning_process: str
    output_conclusion: str
    confidence: float
    evidence: List[str] = field(default_factory=list)

class ReasoningChain:
    \"\"\"分析推理链 - P0最高优先级\"\"\"
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        self.steps = []
        self.final_conclusion = ""
        self.overall_confidence = 0.0
        logger.info(f"🧠 Reasoning Chain initialized: {analysis_id}")
    
    def add_step(self, description: str, input_data: Dict,
                reasoning: str, conclusion: str, 
                confidence: float, evidence: List[str] = None) -> ReasoningStep:
        \"\"\"添加推理步骤\"\"\"
        step = ReasoningStep(
            step_id=f"step_{len(self.steps) + 1}",
            description=description,
            input_data=input_data,
            reasoning_process=reasoning,
            output_conclusion=conclusion,
            confidence=confidence,
            evidence=evidence or []
        )
        
        self.steps.append(step)
        logger.info(f"➕ Added reasoning step: {description}")
        return step
    
    def finalize(self, final_conclusion: str):
        \"\"\"完成推理链\"\"\"
        self.final_conclusion = final_conclusion
        self.overall_confidence = np.mean([s.confidence for s in self.steps]) if self.steps else 0
        
        logger.info(f"✅ Reasoning chain finalized: {final_conclusion}")
    
    def export_chain(self) -> Dict:
        \"\"\"导出完整推理链\"\"\"
        return {
            'analysis_id': self.analysis_id,
            'timestamp': datetime.now().isoformat(),
            'steps': [
                {
                    'step_id': s.step_id,
                    'description': s.description,
                    'reasoning': s.reasoning_process,
                    'conclusion': s.output_conclusion,
                    'confidence': s.confidence,
                    'evidence': s.evidence
                }
                for s in self.steps
            ],
            'final_conclusion': self.final_conclusion,
            'overall_confidence': self.overall_confidence
        }
""",

    "layer3_bias_detector.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L3 P0: 分析偏见检测系统
提出者: Chief Oversight Officer (首席监管官)
\"\"\"
import logging
from typing import Dict, List
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiasType(Enum):
    CONFIRMATION = "确认偏见"      # 只寻找支持自己观点的证据
    SURVIVORSHIP = "幸存者偏见"    # 忽略失败案例
    RECENCY = "近因偏见"          # 过度重视近期事件
    ANCHORING = "锚定偏见"        # 过度依赖第一印象
    OVERCONFIDENCE = "过度自信"   # 高估自己的判断
    HERD = "从众偏见"             # 跟随大众观点

class BiasDetector:
    \"\"\"偏见检测器 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.bias_checks = {}
        logger.info("👁️ Bias Detector initialized")
    
    def detect_confirmation_bias(self, analysis: Dict) -> Dict:
        \"\"\"检测确认偏见\"\"\"
        # 检查是否只引用支持观点的证据
        positive_evidence = len([e for e in analysis.get('evidence', []) 
                                if e.get('supports_thesis', False)])
        negative_evidence = len([e for e in analysis.get('evidence', []) 
                                if not e.get('supports_thesis', True)])
        
        if positive_evidence > 0 and negative_evidence == 0:
            bias_detected = True
            severity = "high"
        elif positive_evidence > negative_evidence * 3:
            bias_detected = True
            severity = "medium"
        else:
            bias_detected = False
            severity = "low"
        
        return {
            'bias_type': BiasType.CONFIRMATION.value,
            'detected': bias_detected,
            'severity': severity,
            'positive_evidence': positive_evidence,
            'negative_evidence': negative_evidence,
            'recommendation': "主动寻找反面证据" if bias_detected else "继续保持"
        }
    
    def detect_recency_bias(self, analysis: Dict) -> Dict:
        \"\"\"检测近因偏见\"\"\"
        # 检查是否过度引用近期数据
        recent_data_weight = analysis.get('recent_data_weight', 0.5)
        
        if recent_data_weight > 0.8:
            bias_detected = True
            severity = "high"
        elif recent_data_weight > 0.6:
            bias_detected = True
            severity = "medium"
        else:
            bias_detected = False
            severity = "low"
        
        return {
            'bias_type': BiasType.RECENCY.value,
            'detected': bias_detected,
            'severity': severity,
            'recent_weight': recent_data_weight,
            'recommendation': "考虑长期历史数据" if bias_detected else "继续保持"
        }
    
    def full_bias_check(self, analysis: Dict) -> List[Dict]:
        \"\"\"完整偏见检查\"\"\"
        results = []
        
        results.append(self.detect_confirmation_bias(analysis))
        results.append(self.detect_recency_bias(analysis))
        
        # 其他偏见检测...
        
        return results
""",

    # L4 - 执行层
    "layer4_decision_audit_log.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L4 P0: 决策审计日志系统
提出者: Chief Architect (顶级架构师)
\"\"\"
import logging
import json
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DecisionRecord:
    decision_id: str
    timestamp: str
    symbol: str
    decision_type: str  # BUY/SELL/HOLD
    quantity: int
    price: float
    reasoning: str
    signals: Dict
    risk_checks: Dict
    confidence: float
    executor: str

class DecisionAuditLog:
    \"\"\"决策审计日志 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.decisions = []
        logger.info("📋 Decision Audit Log initialized")
    
    def record_decision(self, symbol: str, decision_type: str,
                       quantity: int, price: float, reasoning: str,
                       signals: Dict, risk_checks: Dict,
                       confidence: float, executor: str = "A5L") -> DecisionRecord:
        \"\"\"记录决策\"\"\"
        decision = DecisionRecord(
            decision_id=f"dec_{len(self.decisions) + 1}",
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            decision_type=decision_type,
            quantity=quantity,
            price=price,
            reasoning=reasoning,
            signals=signals,
            risk_checks=risk_checks,
            confidence=confidence,
            executor=executor
        )
        
        self.decisions.append(decision)
        
        logger.info(f"📝 Decision recorded: {decision_type} {quantity} {symbol} @ {price}")
        return decision
    
    def query_decisions(self, symbol: str = None, 
                       start_time: str = None,
                       end_time: str = None) -> List[DecisionRecord]:
        \"\"\"查询决策记录\"\"\"
        results = self.decisions
        
        if symbol:
            results = [d for d in results if d.symbol == symbol]
        
        if start_time:
            results = [d for d in results if d.timestamp >= start_time]
        
        if end_time:
            results = [d for d in results if d.timestamp <= end_time]
        
        return results
    
    def export_audit_trail(self, output_path: str):
        \"\"\"导出审计轨迹\"\"\"
        audit_data = [
            {
                'decision_id': d.decision_id,
                'timestamp': d.timestamp,
                'symbol': d.symbol,
                'type': d.decision_type,
                'quantity': d.quantity,
                'price': d.price,
                'reasoning': d.reasoning,
                'confidence': d.confidence
            }
            for d in self.decisions
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Audit trail exported: {output_path}")
""",

    "layer4_risk_circuit_breaker.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L4 P0: 交易风控熔断系统
提出者: Chief Security Officer (安全师)
\"\"\"
import logging
from typing import Dict, List
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # 正常交易
    OPEN = "open"          # 熔断中
    HALF_OPEN = "half_open"  # 试探恢复

class RiskCircuitBreaker:
    \"\"\"风控熔断器 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 300  # 5分钟
        self.last_failure_time = None
        
        # 风控规则
        self.rules = {
            'max_daily_loss': 0.10,      # 单日最大亏损10%
            'max_position_loss': 0.05,   # 单笔最大亏损5%
            'max_drawdown': 0.20,        # 最大回撤20%
            'vix_threshold': 40,         # VIX恐慌指数阈值
        }
        
        logger.info("🛡️ Risk Circuit Breaker initialized")
    
    def check_trade(self, trade: Dict, portfolio: Dict) -> Dict:
        \"\"\"检查交易是否允许\"\"\"
        # 如果熔断中，拒绝交易
        if self.state == CircuitState.OPEN:
            return {
                'allowed': False,
                'reason': '熔断中 - 系统暂停交易',
                'state': self.state.value
            }
        
        # 检查风控规则
        violations = []
        
        # 检查仓位风险
        if trade.get('risk', 0) > self.rules['max_position_loss']:
            violations.append(f"单笔风险{trade['risk']:.1%}超过阈值{self.rules['max_position_loss']:.1%}")
        
        # 检查组合风险
        portfolio_risk = portfolio.get('daily_loss', 0)
        if portfolio_risk > self.rules['max_daily_loss']:
            violations.append(f"日亏损{portfolio_risk:.1%}超过阈值{self.rules['max_daily_loss']:.1%}")
            self._trigger_circuit_breaker("日亏损超限")
        
        return {
            'allowed': len(violations) == 0,
            'violations': violations,
            'state': self.state.value
        }
    
    def _trigger_circuit_breaker(self, reason: str):
        \"\"\"触发熔断\"\"\"
        self.state = CircuitState.OPEN
        self.last_failure_time = datetime.now()
        logger.warning(f"🚨 CIRCUIT BREAKER TRIGGERED: {reason}")
    
    def attempt_reset(self) -> bool:
        \"\"\"尝试重置熔断\"\"\"
        if self.state == CircuitState.OPEN:
            # 检查是否过了冷却期
            # 实际应检查时间
            self.state = CircuitState.HALF_OPEN
            logger.info("🔓 Circuit breaker: HALF_OPEN - 试探恢复")
            return True
        return False
""",

    # L5 - 学习层
    "layer5_review_workflow.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L5 P0: 复盘工作流系统
提出者: Chief Operating Officer (牛逼组织者)
\"\"\"
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReviewTask:
    task_id: str
    type: str  # daily/weekly/monthly
    scheduled_time: str
    status: str  # pending/running/completed
    results: Dict

class ReviewWorkflow:
    \"\"\"复盘工作流 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.tasks = []
        self.templates = {
            'daily': self._daily_template(),
            'weekly': self._weekly_template(),
            'monthly': self._monthly_template()
        }
        logger.info("📊 Review Workflow initialized")
    
    def _daily_template(self) -> List[str]:
        \"\"\"日复盘模板\"\"\"
        return [
            "📈 当日市场表现回顾",
            "💰 账户盈亏分析",
            "🎯 交易执行复盘",
            "📋 策略信号验证",
            "⚠️ 风险事件检查",
            "📚 经验教训总结",
            "🎯 明日计划制定"
        ]
    
    def _weekly_template(self) -> List[str]:
        \"\"\"周复盘模板\"\"\"
        return [
            "📊 周度绩效分析",
            "🎯 策略效果评估",
            "📈 胜率/盈亏比统计",
            "🔄 策略优化建议",
            "📚 知识沉淀归档"
        ]
    
    def _monthly_template(self) -> List[str]:
        \"\"\"月复盘模板\"\"\"
        return [
            "📊 月度综合复盘",
            "💎 VALUE CELL评分回顾",
            "🎯 投资能力归因",
            "📈 复利增长分析",
            "🔄 策略迭代规划",
            "📚 深度研究报告"
        ]
    
    def schedule_review(self, review_type: str, 
                       scheduled_time: str) -> ReviewTask:
        \"\"\"安排复盘任务\"\"\"
        task = ReviewTask(
            task_id=f"review_{len(self.tasks) + 1}",
            type=review_type,
            scheduled_time=scheduled_time,
            status='pending',
            results={}
        )
        
        self.tasks.append(task)
        logger.info(f"📅 Review scheduled: {review_type} at {scheduled_time}")
        return task
    
    def execute_review(self, task_id: str, data: Dict) -> Dict:
        \"\"\"执行复盘\"\"\"
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return {'error': 'Task not found'}
        
        task.status = 'running'
        
        template = self.templates.get(task.type, [])
        results = {
            'template': template,
            'data': data,
            'findings': [],
            'actions': []
        }
        
        # 实际复盘逻辑...
        task.results = results
        task.status = 'completed'
        
        logger.info(f"✅ Review completed: {task_id}")
        return results
""",

    "layer5_attribution_analysis.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
L5 P0: 投资能力归因分析系统
提出者: Chief Investment Officer (顶级投资人)
\"\"\"
import logging
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AttributionResult:
    stock_selection: float      # 选股能力
    market_timing: float        # 择时能力
    sector_allocation: float    # 行业配置能力
    risk_management: float      # 风险管理能力
    luck_factor: float          # 运气成分
    unexplained: float          # 无法解释部分

class AttributionAnalyzer:
    \"\"\"能力归因分析器 - P0最高优先级\"\"\"
    
    def __init__(self):
        self.benchmark = "CSI300"  # 默认基准
        logger.info("📊 Attribution Analyzer initialized")
    
    def analyze_performance(self, portfolio_returns: List[float],
                           benchmark_returns: List[float],
                           trades: List[Dict]) -> AttributionResult:
        \"\"\"分析绩效归因\"\"\"
        # 计算总收益
        portfolio_total = np.prod([1 + r for r in portfolio_returns]) - 1
        benchmark_total = np.prod([1 + r for r in benchmark_returns]) - 1
        excess_return = portfolio_total - benchmark_total
        
        # 归因分析 (简化版)
        # 实际应使用Brinson模型或多因子模型
        
        # 选股能力 (个股选择带来的超额收益)
        stock_selection = excess_return * 0.4  # 假设40%来自选股
        
        # 择时能力 (仓位调整带来的超额收益)
        market_timing = excess_return * 0.25   # 假设25%来自择时
        
        # 行业配置
        sector_allocation = excess_return * 0.20  # 假设20%来自行业配置
        
        # 风险管理 (风险控制带来的稳定收益)
        portfolio_vol = np.std(portfolio_returns)
        benchmark_vol = np.std(benchmark_returns)
        risk_adjusted = (portfolio_total / portfolio_vol) - (benchmark_total / benchmark_vol)
        risk_management = risk_adjusted * 0.1  # 假设10%来自风险管理
        
        # 运气成分 (随机性)
        luck_factor = excess_return * 0.03    # 假设3%是运气
        
        # 无法解释
        unexplained = excess_return - (stock_selection + market_timing + 
                                      sector_allocation + risk_management + luck_factor)
        
        return AttributionResult(
            stock_selection=stock_selection,
            market_timing=market_timing,
            sector_allocation=sector_allocation,
            risk_management=risk_management,
            luck_factor=luck_factor,
            unexplained=unexplained
        )
    
    def generate_attribution_report(self, result: AttributionResult) -> str:
        \"\"\"生成归因报告\"\"\"
        total = (result.stock_selection + result.market_timing + 
                result.sector_allocation + result.risk_management + 
                result.luck_factor + result.unexplained)
        
        lines = [
            "# 📊 投资能力归因分析报告",
            "",
            "## 归因分解",
            "",
            f"| 能力维度 | 贡献收益 | 占比 |",
            f"|----------|----------|------|",
            f"| 📈 选股能力 | {result.stock_selection:.2%} | {result.stock_selection/total:.1%} |",
            f"| ⏰ 择时能力 | {result.market_timing:.2%} | {result.market_timing/total:.1%} |",
            f"| 🏭 行业配置 | {result.sector_allocation:.2%} | {result.sector_allocation/total:.1%} |",
            f"| 🛡️ 风险管理 | {result.risk_management:.2%} | {result.risk_management/total:.1%} |",
            f"| 🍀 运气成分 | {result.luck_factor:.2%} | {result.luck_factor/total:.1%} |",
            f"| ❓ 无法解释 | {result.unexplained:.2%} | {result.unexplained/total:.1%} |",
            "",
            "## 核心能力识别",
            ""
        ]
        
        # 识别最强能力
        abilities = {
            '选股能力': result.stock_selection,
            '择时能力': result.market_timing,
            '行业配置': result.sector_allocation,
            '风险管理': result.risk_management
        }
        strongest = max(abilities, key=abilities.get)
        
        lines.append(f"**核心优势**: {strongest} (贡献{abilities[strongest]:.2%}超额收益)")
        lines.append("")
        lines.append("## 改进建议")
        lines.append("")
        
        # 找出最弱能力
        weakest = min(abilities, key=abilities.get)
        lines.append(f"- 重点提升: {weakest} 能力")
        lines.append(f"- 保持优势: {strongest} 能力")
        
        return '\n'.join(lines)
""",
}

# 创建所有文件
output_dir = "/workspace/projects/workspace/ARCHITECT_5L/p0_skills"
os.makedirs(output_dir, exist_ok=True)

for filename, content in SKILLS_TO_CREATE.items():
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filename}")

print(f"\n🎉 All {len(SKILLS_TO_CREATE)} P0 skills created!")
print(f"📁 Location: {output_dir}")
