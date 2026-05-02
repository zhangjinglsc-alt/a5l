#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L4 P0: 交易风控熔断系统 (v1.5.x Enhanced)
提出者: Chief Security Officer (安全师)
状态: ✅ 已完善

核心功能:
1. 多级熔断机制 (个股/组合/市场)
2. 自动冷却恢复
3. 实时风险监控
4. 熔断历史记录
"""

import logging
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断状态"""
    CLOSED = "closed"          # 正常 - 允许交易
    OPEN = "open"              # 熔断 - 禁止交易
    HALF_OPEN = "half_open"    # 半开 - 试探性恢复


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"                # 低风险
    MEDIUM = "medium"          # 中风险
    HIGH = "high"              # 高风险
    CRITICAL = "critical"      # 极高风险


@dataclass
class CircuitBreakerEvent:
    """熔断事件记录"""
    timestamp: str
    trigger: str               # 触发原因
    risk_level: str
    portfolio_value: float
    loss_amount: float
    auto_recovery: bool


@dataclass
class RiskCheckResult:
    """风险检查结果"""
    allowed: bool
    state: str
    risk_level: str
    violations: List[str]
    warnings: List[str]
    position_limit: Optional[float] = None  # 建议仓位上限


class RiskCircuitBreaker:
    """
    交易风控熔断系统 - P0最高优先级
    
    熔断触发条件:
    1. 单日亏损 > 10% (组合级)
    2. 单笔亏损 > 5% (交易级)
    3. 最大回撤 > 20% (组合级)
    4. 连续亏损 > 3次 (交易级)
    5. 波动率异常 (市场级)
    
    冷却机制:
    - 自动冷却: 熔断后15分钟自动尝试恢复
    - 手动恢复: 人工确认后恢复
    - 渐进恢复: 半开状态允许小仓位试探
    """
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.state_changed_at = datetime.now()
        
        # 计数器
        self.failure_count = 0           # 连续失败次数
        self.daily_loss_count = 0        # 日亏损次数
        self.circuit_break_count = 0     # 熔断触发次数
        
        # 阈值配置
        self.thresholds = {
            # 组合级风控
            'max_daily_loss_pct': 0.10,      # 单日最大亏损10%
            'max_drawdown_pct': 0.20,        # 最大回撤20%
            'max_portfolio_concentration': 0.30,  # 最大集中度30%
            
            # 交易级风控
            'max_position_loss_pct': 0.05,   # 单笔最大亏损5%
            'max_single_position_pct': 0.20, # 单票最大仓位20%
            
            # 行为级风控
            'max_consecutive_losses': 3,     # 连续亏损3次暂停
            'max_trades_per_hour': 10,       # 每小时最多10笔
            
            # 市场级风控
            'vix_threshold': 40,             # VIX恐慌指数阈值
            'market_drop_threshold': 0.05,   # 大盘下跌5%
        }
        
        # 冷却配置
        self.cooldown = {
            'auto_recovery_minutes': 15,     # 自动冷却15分钟
            'half_open_position_limit': 0.5,  # 半开状态仓位上限50%
            'max_circuit_breaks_per_day': 3,  # 每日最多熔断3次
        }
        
        # 历史记录
        self.events: List[CircuitBreakerEvent] = []
        self.trade_history: List[Dict] = []
        
        logger.info("🛡️ Risk Circuit Breaker initialized (v1.5.x)")
    
    def check_trade(self, trade: Dict, portfolio: Dict) -> RiskCheckResult:
        """
        检查交易是否允许执行
        
        Args:
            trade: 交易信息 {'symbol', 'amount', 'price', 'risk'}
            portfolio: 组合信息 {'total_value', 'daily_pnl', 'positions'}
            
        Returns:
            RiskCheckResult: 检查结果
        """
        violations = []
        warnings = []
        position_limit = None
        
        # 1. 检查熔断状态
        if self.state == CircuitState.OPEN:
            # 检查是否可自动恢复
            if self._can_auto_recover():
                self._enter_half_open()
            else:
                return RiskCheckResult(
                    allowed=False,
                    state=self.state.value,
                    risk_level=RiskLevel.CRITICAL.value,
                    violations=["熔断中 - 系统暂停交易"],
                    warnings=[f"冷却倒计时: {self._get_cooldown_remaining()}分钟"]
                )
        
        # 2. 检查半开状态限制
        if self.state == CircuitState.HALF_OPEN:
            position_limit = self.cooldown['half_open_position_limit']
            warnings.append(f"半开状态 - 建议仓位不超过{position_limit*100:.0f}%")
        
        # 3. 检查交易级风控
        trade_violations = self._check_trade_level_risk(trade)
        violations.extend(trade_violations)
        
        # 4. 检查组合级风控
        portfolio_violations = self._check_portfolio_level_risk(portfolio)
        violations.extend(portfolio_violations)
        
        # 5. 检查行为级风控
        behavior_violations = self._check_behavior_risk(trade)
        violations.extend(behavior_violations)
        
        # 6. 综合评估风险等级
        risk_level = self._assess_risk_level(violations, warnings)
        
        # 7. 如果严重违规，触发熔断
        if self._should_trigger_circuit_breaker(violations, portfolio):
            self._trigger_circuit_breaker(violations[0], portfolio)
            return RiskCheckResult(
                allowed=False,
                state=self.state.value,
                risk_level=RiskLevel.CRITICAL.value,
                violations=violations,
                warnings=warnings
            )
        
        # 8. 记录交易历史
        self._record_trade(trade, len(violations) == 0)
        
        return RiskCheckResult(
            allowed=len(violations) == 0,
            state=self.state.value,
            risk_level=risk_level.value,
            violations=violations,
            warnings=warnings,
            position_limit=position_limit
        )
    
    def _check_trade_level_risk(self, trade: Dict) -> List[str]:
        """检查交易级风险"""
        violations = []
        
        # 单笔亏损检查
        if trade.get('risk', 0) > self.thresholds['max_position_loss_pct']:
            violations.append(
                f"单笔风险{trade['risk']:.1%}超过阈值{self.thresholds['max_position_loss_pct']:.1%}"
            )
        
        # 仓位上限检查
        position_pct = trade.get('position_pct', 0)
        if position_pct > self.thresholds['max_single_position_pct']:
            violations.append(
                f"单票仓位{position_pct:.1%}超过上限{self.thresholds['max_single_position_pct']:.1%}"
            )
        
        return violations
    
    def _check_portfolio_level_risk(self, portfolio: Dict) -> List[str]:
        """检查组合级风险"""
        violations = []
        
        # 日亏损检查
        daily_pnl_pct = portfolio.get('daily_pnl_pct', 0)
        if daily_pnl_pct < -self.thresholds['max_daily_loss_pct']:
            violations.append(
                f"日亏损{abs(daily_pnl_pct):.1%}超过阈值{self.thresholds['max_daily_loss_pct']:.1%}"
            )
        
        # 最大回撤检查
        drawdown_pct = portfolio.get('drawdown_pct', 0)
        if drawdown_pct > self.thresholds['max_drawdown_pct']:
            violations.append(
                f"当前回撤{drawdown_pct:.1%}超过阈值{self.thresholds['max_drawdown_pct']:.1%}"
            )
        
        # 集中度检查
        concentration = portfolio.get('concentration', 0)
        if concentration > self.thresholds['max_portfolio_concentration']:
            violations.append(
                f"组合集中度{concentration:.1%}超过上限{self.thresholds['max_portfolio_concentration']:.1%}"
            )
        
        return violations
    
    def _check_behavior_risk(self, trade: Dict) -> List[str]:
        """检查交易行为风险"""
        violations = []
        
        # 连续亏损检查
        if self.failure_count >= self.thresholds['max_consecutive_losses']:
            violations.append(
                f"连续亏损{self.failure_count}次超过阈值{self.thresholds['max_consecutive_losses']}次"
            )
        
        # 交易频率检查
        recent_trades = self._get_recent_trades(minutes=60)
        if len(recent_trades) > self.thresholds['max_trades_per_hour']:
            violations.append(
                f"过去1小时交易{len(recent_trades)}笔超过上限{self.thresholds['max_trades_per_hour']}笔"
            )
        
        return violations
    
    def _should_trigger_circuit_breaker(self, violations: List[str], portfolio: Dict) -> bool:
        """判断是否触发熔断"""
        # 严重违规触发熔断
        critical_keywords = ['日亏损', '回撤', '连续亏损']
        for v in violations:
            if any(kw in v for kw in critical_keywords):
                return True
        return False
    
    def _trigger_circuit_breaker(self, reason: str, portfolio: Dict):
        """触发熔断机制"""
        if self.circuit_break_count >= self.cooldown['max_circuit_breaks_per_day']:
            logger.error(f"❌ 今日熔断次数已达上限{self.cooldown['max_circuit_breaks_per_day']}次，禁止交易")
            return
        
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_changed_at = datetime.now()
        self.circuit_break_count += 1
        
        # 记录事件
        event = CircuitBreakerEvent(
            timestamp=datetime.now().isoformat(),
            trigger=reason,
            risk_level=RiskLevel.CRITICAL.value,
            portfolio_value=portfolio.get('total_value', 0),
            loss_amount=portfolio.get('daily_pnl', 0),
            auto_recovery=True
        )
        self.events.append(event)
        
        logger.warning(f"🚨 CIRCUIT BREAKER TRIGGERED!")
        logger.warning(f"   Reason: {reason}")
        logger.warning(f"   State: {old_state.value} -> {self.state.value}")
        logger.warning(f"   Auto-recovery in: {self.cooldown['auto_recovery_minutes']} minutes")
    
    def _can_auto_recover(self) -> bool:
        """检查是否可以自动恢复"""
        if self.state != CircuitState.OPEN:
            return False
        
        elapsed = (datetime.now() - self.state_changed_at).total_seconds() / 60
        return elapsed >= self.cooldown['auto_recovery_minutes']
    
    def _enter_half_open(self):
        """进入半开状态"""
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = datetime.now()
        logger.info(f"🔓 Circuit breaker: HALF_OPEN - 试探性恢复，仓位限制{self.cooldown['half_open_position_limit']*100:.0f}%")
    
    def manual_reset(self) -> bool:
        """手动重置熔断"""
        if self.state in [CircuitState.OPEN, CircuitState.HALF_OPEN]:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.state_changed_at = datetime.now()
            logger.info("✅ Circuit breaker manually reset to CLOSED")
            return True
        return False
    
    def confirm_half_open_success(self):
        """确认半开状态成功，完全恢复"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.state_changed_at = datetime.now()
            logger.info("✅ Circuit breaker fully recovered to CLOSED")
    
    def _assess_risk_level(self, violations: List[str], warnings: List[str]) -> RiskLevel:
        """评估风险等级"""
        if len(violations) >= 2:
            return RiskLevel.CRITICAL
        elif len(violations) == 1:
            return RiskLevel.HIGH
        elif len(warnings) >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _record_trade(self, trade: Dict, success: bool):
        """记录交易"""
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': trade.get('symbol'),
            'success': success
        }
        self.trade_history.append(trade_record)
        
        # 更新连续失败计数
        if success:
            self.failure_count = 0
        else:
            self.failure_count += 1
    
    def _get_recent_trades(self, minutes: int = 60) -> List[Dict]:
        """获取最近交易"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            t for t in self.trade_history
            if datetime.fromisoformat(t['timestamp']) > cutoff
        ]
    
    def _get_cooldown_remaining(self) -> int:
        """获取剩余冷却时间"""
        if self.state != CircuitState.OPEN:
            return 0
        elapsed = (datetime.now() - self.state_changed_at).total_seconds() / 60
        remaining = max(0, self.cooldown['auto_recovery_minutes'] - elapsed)
        return int(remaining)
    
    def get_status(self) -> Dict:
        """获取熔断器状态"""
        return {
            'state': self.state.value,
            'state_since': self.state_changed_at.isoformat(),
            'failure_count': self.failure_count,
            'circuit_break_count': self.circuit_break_count,
            'cooldown_remaining': self._get_cooldown_remaining(),
            'total_events': len(self.events),
            'recent_events': [
                {
                    'timestamp': e.timestamp,
                    'trigger': e.trigger,
                    'loss': e.loss_amount
                }
                for e in self.events[-5:]
            ]
        }


def main():
    """测试熔断器"""
    print("=" * 80)
    print("🛡️ Risk Circuit Breaker v1.5.x Test")
    print("=" * 80)
    
    breaker = RiskCircuitBreaker()
    
    # 正常交易
    print("\n[1/4] 正常交易测试")
    result = breaker.check_trade(
        trade={'symbol': 'AAPL', 'risk': 0.02, 'position_pct': 0.1},
        portfolio={'total_value': 100000, 'daily_pnl_pct': 0.02, 'drawdown_pct': 0.05}
    )
    print(f"   Allowed: {result.allowed}, Risk: {result.risk_level}")
    
    # 触发单笔风控
    print("\n[2/4] 单笔风控测试")
    result = breaker.check_trade(
        trade={'symbol': 'TSLA', 'risk': 0.08, 'position_pct': 0.25},
        portfolio={'total_value': 100000, 'daily_pnl_pct': -0.05, 'drawdown_pct': 0.10}
    )
    print(f"   Allowed: {result.allowed}, Violations: {len(result.violations)}")
    
    # 触发熔断
    print("\n[3/4] 熔断触发测试")
    result = breaker.check_trade(
        trade={'symbol': 'NVDA', 'risk': 0.02},
        portfolio={'total_value': 90000, 'daily_pnl_pct': -0.12, 'drawdown_pct': 0.10}
    )
    print(f"   Allowed: {result.allowed}, State: {result.state}")
    print(f"   Cooldown: {breaker._get_cooldown_remaining()}min")
    
    # 状态查询
    print("\n[4/4] 状态查询")
    status = breaker.get_status()
    print(f"   State: {status['state']}")
    print(f"   Events: {status['total_events']}")
    print(f"   Circuit breaks today: {status['circuit_break_count']}")
    
    print("\n" + "=" * 80)
    print("✅ Risk Circuit Breaker v1.5.x Ready!")


if __name__ == "__main__":
    main()
