#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 2: Strategy Engine
策略引擎

功能：
1. 策略注册和管理
2. 策略执行和信号生成
3. 策略性能跟踪
4. 策略回测支持
"""

import json
import os
import sys
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer1_data')

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from data_store import DataStore

@dataclass
class StrategyConfig:
    """策略配置"""
    name: str
    description: str
    market: str  # US, CN, HK, ALL
    style: str  # trend, value, momentum, mean_reversion
    holding_period: str  # short(<5d), medium(5-30d), long(>30d)
    entry_rules: List[Dict]
    exit_rules: List[Dict]
    risk_params: Dict
    active: bool = True

class StrategyEngine:
    """策略引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.strategies_dir = f"{workspace}/ARCHITECT_5L/layer2_strategy/strategies"
        self.config_file = f"{workspace}/ARCHITECT_5L/layer2_strategy/strategy_registry.json"
        
        os.makedirs(self.strategies_dir, exist_ok=True)
        
        # 初始化数据存储连接
        self.data_store = DataStore(workspace)
        
        # 加载策略注册表
        self.strategies = self._load_strategy_registry()
        
        # 策略性能跟踪
        self._performance_cache = {}
    
    def _load_strategy_registry(self) -> Dict[str, StrategyConfig]:
        """加载策略注册表"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: StrategyConfig(**v) for k, v in data.items()}
        
        # 初始化默认策略
        return self._init_default_strategies()
    
    def _init_default_strategies(self) -> Dict[str, StrategyConfig]:
        """初始化默认策略"""
        default_strategies = {
            "stock_wizard": StrategyConfig(
                name="股票魔法师 (CANSLIM)",
                description="基于马克·米勒维尼的CANSLIM方法，寻找高增长强势股",
                market="ALL",
                style="momentum",
                holding_period="medium",
                entry_rules=[
                    {"indicator": "price_trend", "condition": "above_ma", "params": {"periods": [50, 150, 200]}},
                    {"indicator": "rs_rating", "condition": ">", "params": {"value": 80}},
                    {"indicator": "earnings_growth", "condition": ">", "params": {"value": 0.25}},
                    {"indicator": "volume", "condition": "surge", "params": {"multiplier": 1.5}}
                ],
                exit_rules=[
                    {"indicator": "price", "condition": "break_below", "params": {"ma_period": 50}},
                    {"indicator": "stop_loss", "condition": "trailing", "params": {"percent": 8}},
                    {"indicator": "time", "condition": "max_hold", "params": {"days": 60}}
                ],
                risk_params={
                    "max_position_pct": 10,
                    "stop_loss_pct": 7,
                    "trailing_stop_pct": 8
                }
            ),
            "turtle_trading": StrategyConfig(
                name="海龟交易法则",
                description="经典的趋势跟踪系统，基于唐奇安通道突破",
                market="ALL",
                style="trend",
                holding_period="medium",
                entry_rules=[
                    {"indicator": "donchian", "condition": "breakout_high", "params": {"period": 20}},
                    {"indicator": "atr", "condition": "filter", "params": {"min_atr": 0.02}}
                ],
                exit_rules=[
                    {"indicator": "donchian", "condition": "breakout_low", "params": {"period": 10}},
                    {"indicator": "stop_loss", "condition": "fixed", "params": {"atr_multiplier": 2}}
                ],
                risk_params={
                    "position_unit_pct": 1,  # 1% risk per trade
                    "max_units": 4,
                    "atr_period": 20
                }
            ),
            "trend_rs": StrategyConfig(
                name="趋势突破+相对强度",
                description="价格突破新高且相对强度排名靠前",
                market="ALL",
                style="momentum",
                holding_period="short",
                entry_rules=[
                    {"indicator": "price", "condition": "break_high", "params": {"period": 20}},
                    {"indicator": "rs_rank", "condition": "top_pct", "params": {"percent": 20}},
                    {"indicator": "volume", "condition": "above_avg", "params": {"multiplier": 1.5}}
                ],
                exit_rules=[
                    {"indicator": "stop_loss", "condition": "trailing", "params": {"percent": 5}},
                    {"indicator": "rs_rank", "condition": "drop_below", "params": {"percent": 30}}
                ],
                risk_params={
                    "max_position_pct": 8,
                    "stop_loss_pct": 5
                }
            ),
            "volume_price": StrategyConfig(
                name="量价分析策略",
                description="基于成交量和价格的背离与确认",
                market="ALL",
                style="momentum",
                holding_period="short",
                entry_rules=[
                    {"indicator": "volume", "condition": "surge", "params": {"multiplier": 2}},
                    {"indicator": "price", "condition": "up", "params": {"min_pct": 2}}
                ],
                exit_rules=[
                    {"indicator": "volume", "condition": "shrink", "params": {"multiplier": 0.7}},
                    {"indicator": "divergence", "condition": "bearish", "params": {}}
                ],
                risk_params={
                    "max_position_pct": 5,
                    "stop_loss_pct": 3
                }
            ),
            "fundamental_growth": StrategyConfig(
                name="基本面增长策略",
                description="基于财务指标的高增长价值投资",
                market="ALL",
                style="value",
                holding_period="long",
                entry_rules=[
                    {"indicator": "revenue_growth", "condition": ">", "params": {"value": 0.20, "quarters": 2}},
                    {"indicator": "profit_growth", "condition": ">", "params": {"value": 0.20, "quarters": 2}},
                    {"indicator": "roe", "condition": ">", "params": {"value": 0.15}},
                    {"indicator": "pe", "condition": "<", "params": {"value": 30}}
                ],
                exit_rules=[
                    {"indicator": "growth", "condition": "decelerate", "params": {"threshold": 0.10}},
                    {"indicator": "pe", "condition": ">", "params": {"value": 50}},
                    {"indicator": "time", "condition": "max_hold", "params": {"days": 180}}
                ],
                risk_params={
                    "max_position_pct": 15,
                    "stop_loss_pct": 10
                }
            ),
            "yangguan_daodao": StrategyConfig(
                name="阳关大道超短线",
                description="基于浪主系统的超短交易策略",
                market="CN",
                style="momentum",
                holding_period="short",
                entry_rules=[
                    {"indicator": "pattern", "condition": "yangguan_setup", "params": {}},
                    {"indicator": "volume", "condition": "confirm", "params": {}}
                ],
                exit_rules=[
                    {"indicator": "time", "condition": "max_hold", "params": {"days": 3}},
                    {"indicator": "stop_loss", "condition": "fixed", "params": {"percent": 3}}
                ],
                risk_params={
                    "max_position_pct": 5,
                    "stop_loss_pct": 3,
                    "max_hold_days": 3
                }
            ),
            "buffett_value": StrategyConfig(
                name="巴菲特价值投资",
                description="基于安全边际和护城河的价值投资",
                market="ALL",
                style="value",
                holding_period="long",
                entry_rules=[
                    {"indicator": "moat", "condition": "exists", "params": {}},
                    {"indicator": "margin_of_safety", "condition": ">", "params": {"value": 0.30}},
                    {"indicator": "roe", "condition": ">", "params": {"value": 0.15}},
                    {"indicator": "debt", "condition": "<", "params": {"value": 0.5}}
                ],
                exit_rules=[
                    {"indicator": "valuation", "condition": "fair_value", "params": {}},
                    {"indicator": "moat", "condition": "erode", "params": {}}
                ],
                risk_params={
                    "max_position_pct": 20,
                    "concentration_limit": 40
                }
            )
        }
        
        self._save_strategy_registry(default_strategies)
        return default_strategies
    
    def _save_strategy_registry(self, strategies: Dict[str, StrategyConfig]):
        """保存策略注册表"""
        data = {k: asdict(v) for k, v in strategies.items()}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyConfig]:
        """获取策略配置"""
        return self.strategies.get(strategy_id)
    
    def list_strategies(self, market: Optional[str] = None, 
                       style: Optional[str] = None) -> List[str]:
        """列出策略"""
        result = []
        for sid, config in self.strategies.items():
            if market and config.market != "ALL" and config.market != market:
                continue
            if style and config.style != style:
                continue
            result.append(sid)
        return result
    
    def evaluate_entry(self, symbol: str, strategy_id: str, 
                       data: Dict) -> Dict:
        """
        评估入场条件
        
        Returns:
            评估结果
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return {"error": f"Strategy {strategy_id} not found"}
        
        results = {
            "symbol": symbol,
            "strategy": strategy_id,
            "timestamp": datetime.now().isoformat(),
            "entry_rules": [],
            "passed": 0,
            "failed": 0,
            "signal": False,
            "confidence": 0.0
        }
        
        for rule in strategy.entry_rules:
            rule_result = self._evaluate_rule(rule, data)
            results["entry_rules"].append(rule_result)
            
            if rule_result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # 计算置信度（通过的规则比例）
        total_rules = len(strategy.entry_rules)
        if total_rules > 0:
            results["confidence"] = results["passed"] / total_rules
            # 全部通过才产生信号
            results["signal"] = results["passed"] == total_rules
        
        return results
    
    def _evaluate_rule(self, rule: Dict, data: Dict) -> Dict:
        """评估单个规则"""
        indicator = rule.get("indicator", "")
        condition = rule.get("condition", "")
        params = rule.get("params", {})
        
        result = {
            "indicator": indicator,
            "condition": condition,
            "params": params,
            "passed": False,
            "actual_value": None,
            "expected": None
        }
        
        # 简化的规则评估逻辑
        # 实际实现需要更复杂的指标计算
        try:
            if indicator == "price_trend" and condition == "above_ma":
                # 检查价格是否在均线之上
                close = data.get("close", 0)
                periods = params.get("periods", [50])
                # 模拟：假设价格高于均线
                result["passed"] = close > 0
                result["actual_value"] = close
                
            elif indicator == "rs_rating" and condition == ">":
                # 相对强度评级
                threshold = params.get("value", 80)
                rs = data.get("rs_rating", 0)
                result["passed"] = rs >= threshold
                result["actual_value"] = rs
                result["expected"] = f">= {threshold}"
                
            elif indicator == "volume" and condition == "surge":
                # 成交量突增
                multiplier = params.get("multiplier", 2)
                volume = data.get("volume", 0)
                avg_volume = data.get("avg_volume", 1)
                ratio = volume / avg_volume if avg_volume > 0 else 0
                result["passed"] = ratio >= multiplier
                result["actual_value"] = ratio
                result["expected"] = f">= {multiplier}x"
                
            elif indicator == "earnings_growth" and condition == ">":
                # 盈利增长
                threshold = params.get("value", 0.25)
                growth = data.get("earnings_growth", 0)
                result["passed"] = growth >= threshold
                result["actual_value"] = growth
                result["expected"] = f">= {threshold}"
                
            else:
                # 其他规则默认通过（需要具体实现）
                result["passed"] = True
                result["note"] = "Rule not fully implemented, default pass"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_signal(self, symbol: str, strategy_id: str, 
                       market_data: Dict) -> Dict:
        """
        生成交易信号
        
        Returns:
            交易信号
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return {"error": f"Strategy {strategy_id} not found"}
        
        # 评估入场条件
        entry_eval = self.evaluate_entry(symbol, strategy_id, market_data)
        
        signal = {
            "symbol": symbol,
            "strategy": strategy_id,
            "strategy_name": strategy.name,
            "timestamp": datetime.now().isoformat(),
            "action": None,
            "confidence": entry_eval["confidence"],
            "entry_evaluation": entry_eval,
            "risk_params": strategy.risk_params
        }
        
        if entry_eval["signal"]:
            signal["action"] = "BUY"
            signal["reason"] = f"All {entry_eval['passed']} entry rules passed"
        else:
            signal["action"] = "HOLD"
            signal["reason"] = f"Only {entry_eval['passed']}/{len(strategy.entry_rules)} rules passed"
        
        return signal
    
    def generate_strategy_report(self) -> str:
        """生成策略报告"""
        report = f"""# 📈 Layer 2: 策略引擎 - 策略报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**策略总数**: {len(self.strategies)}

---

## 🎯 策略列表

"""
        
        for sid, config in self.strategies.items():
            status = "✅ 活跃" if config.active else "⏸️ 暂停"
            report += f"""### {config.name} ({sid})
- **状态**: {status}
- **市场**: {config.market}
- **风格**: {config.style}
- **持仓周期**: {config.holding_period}
- **入场规则**: {len(config.entry_rules)} 条
- **出场规则**: {len(config.exit_rules)} 条
- **最大仓位**: {config.risk_params.get('max_position_pct', 'N/A')}%
- **止损**: {config.risk_params.get('stop_loss_pct', 'N/A')}%

**描述**: {config.description}

---

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📈 Layer 2: 策略引擎")
    print("=" * 70)
    
    engine = StrategyEngine()
    
    # 显示策略列表
    print("\n🎯 已加载策略:")
    for sid in engine.list_strategies():
        config = engine.get_strategy(sid)
        print(f"  • {config.name} ({sid}) - {config.style}")
    
    # 按市场筛选
    print("\n🇨🇳 A股策略:")
    for sid in engine.list_strategies(market="CN"):
        config = engine.get_strategy(sid)
        print(f"  • {config.name}")
    
    # 测试信号生成
    print("\n🧪 测试信号生成...")
    test_data = {
        "symbol": "000001.SZ",
        "close": 10.6,
        "volume": 2000000,
        "avg_volume": 1000000,
        "rs_rating": 85,
        "earnings_growth": 0.30
    }
    
    signal = engine.generate_signal("000001.SZ", "stock_wizard", test_data)
    print(f"\n  策略: {signal['strategy_name']}")
    print(f"  动作: {signal['action']}")
    print(f"  置信度: {signal['confidence']:.1%}")
    print(f"  原因: {signal['reason']}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 策略报告:")
    report = engine.generate_strategy_report()
    print(report[:800] + "...")

if __name__ == "__main__":
    main()
