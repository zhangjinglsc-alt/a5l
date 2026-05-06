#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Rules & Strategy Engine
交易规则与策略引擎

功能：
1. 制定交易规则（选股、入场、出场、风控）
2. 多策略支持（趋势跟随、均值回归、动量、突破）
3. 自适应参数调整
4. 跨市场策略适配
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TradingRule:
    """交易规则"""
    name: str
    market: str  # US/CN/HK
    strategy_type: str
    entry_conditions: List[Dict]
    exit_conditions: List[Dict]
    risk_params: Dict
    position_sizing: Dict
    active: bool = True

class TradingRulesEngine:
    """交易规则引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.rules_file = f"{workspace}/data/trading_rules/active_rules.json"
        self.strategies_file = f"{workspace}/data/trading_rules/strategies.json"
        
        os.makedirs(f"{workspace}/data/trading_rules", exist_ok=True)
        
        self.rules = self._load_rules()
        self.strategies = self._load_strategies()
        
        if not self.rules:
            self._init_default_rules()
    
    def _load_rules(self) -> List[Dict]:
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_strategies(self) -> Dict:
        if os.path.exists(self.strategies_file):
            with open(self.strategies_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_rules(self):
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
    
    def _init_default_rules(self):
        """初始化默认交易规则"""
        self.rules = [
            {
                "rule_id": "RULE-US-001",
                "name": "美股动量突破策略",
                "market": "US",
                "strategy_type": "momentum_breakout",
                "description": "基于20日新高突破的动量策略",
                "entry_conditions": [
                    {"indicator": "price", "condition": "breaks_above", "period": 20, "lookback": "days"},
                    {"indicator": "volume", "condition": "above_average", "period": 20, "multiplier": 1.5},
                    {"indicator": "rsi", "condition": "between", "min": 50, "max": 70}
                ],
                "exit_conditions": [
                    {"type": "stop_loss", "pct": 5.0},
                    {"type": "take_profit", "pct": 15.0},
                    {"type": "trailing_stop", "pct": 8.0},
                    {"type": "time_exit", "days": 20}
                ],
                "risk_params": {
                    "max_position_pct": 15.0,
                    "max_daily_trades": 3,
                    "max_consecutive_losses": 2
                },
                "position_sizing": {
                    "method": "fixed_pct",
                    "pct_per_trade": 10.0,
                    "max_total_exposure": 60.0
                },
                "active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "rule_id": "RULE-CN-001",
                "name": "A股趋势跟随策略",
                "market": "CN",
                "strategy_type": "trend_following",
                "description": "基于均线系统的中期趋势跟随",
                "entry_conditions": [
                    {"indicator": "ma", "condition": "golden_cross", "fast": 5, "slow": 20},
                    {"indicator": "macd", "condition": "bullish_cross"},
                    {"indicator": "volume", "condition": "above_average", "period": 5, "multiplier": 1.2}
                ],
                "exit_conditions": [
                    {"type": "stop_loss", "pct": 5.0},
                    {"type": "take_profit", "pct": 12.0},
                    {"type": "ma_cross", "fast": 5, "slow": 20, "direction": "death_cross"},
                    {"type": "limit_up", "action": "partial_sell", "pct": 50}
                ],
                "risk_params": {
                    "max_position_pct": 12.0,
                    "max_daily_trades": 5,
                    "limit_up_protection": True,
                    "limit_down_protection": True
                },
                "position_sizing": {
                    "method": "volatility_adjusted",
                    "base_pct": 8.0,
                    "atr_multiplier": 2.0
                },
                "active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "rule_id": "RULE-HK-001",
                "name": "港股价值投资策略",
                "market": "HK",
                "strategy_type": "value_investing",
                "description": "基于估值修复的价值投资策略",
                "entry_conditions": [
                    {"indicator": "pe", "condition": "below", "value": 15},
                    {"indicator": "pb", "condition": "below", "value": 1.5},
                    {"indicator": "dividend_yield", "condition": "above", "value": 3.0},
                    {"indicator": "price", "condition": "above", "ma_period": 60}
                ],
                "exit_conditions": [
                    {"type": "stop_loss", "pct": 8.0},
                    {"type": "pe_target", "value": 20},
                    {"type": "pb_target", "value": 2.0},
                    {"type": "time_exit", "days": 90}
                ],
                "risk_params": {
                    "max_position_pct": 20.0,
                    "max_daily_trades": 2,
                    "sector_concentration_limit": 40.0
                },
                "position_sizing": {
                    "method": "fixed_pct",
                    "pct_per_trade": 15.0
                },
                "active": True,
                "created_at": datetime.now().isoformat()
            }
        ]
        self._save_rules()
    
    def get_active_rules(self, market: Optional[str] = None) -> List[Dict]:
        """获取活跃规则"""
        rules = [r for r in self.rules if r.get('active', False)]
        if market:
            rules = [r for r in rules if r['market'] == market]
        return rules
    
    def generate_signal(self, symbol: str, market: str, price_data: Dict) -> Optional[Dict]:
        """生成交易信号"""
        rules = self.get_active_rules(market)
        if not rules:
            return None
        
        # 使用第一个匹配的规则
        rule = rules[0]
        
        # 模拟信号生成（实际应该基于技术指标计算）
        import random
        if random.random() < 0.1:  # 10%概率生成信号
            signal = {
                "symbol": symbol,
                "market": market,
                "action": "BUY" if random.random() > 0.3 else "SELL",
                "strategy": rule['strategy_type'],
                "rule_id": rule['rule_id'],
                "confidence": random.uniform(0.6, 0.9),
                "suggested_shares": random.randint(100, 500),
                "timestamp": datetime.now().isoformat(),
                "reason": f"触发{rule['name']}条件"
            }
            return signal
        
        return None
    
    def update_rule_performance(self, rule_id: str, trade_result: Dict):
        """更新规则表现"""
        for rule in self.rules:
            if rule['rule_id'] == rule_id:
                if 'performance' not in rule:
                    rule['performance'] = {
                        "total_trades": 0,
                        "winning_trades": 0,
                        "total_pnl": 0.0,
                        "win_rate": 0.0
                    }
                
                perf = rule['performance']
                perf['total_trades'] += 1
                
                if trade_result.get('pnl', 0) > 0:
                    perf['winning_trades'] += 1
                
                perf['total_pnl'] += trade_result.get('pnl', 0)
                perf['win_rate'] = perf['winning_trades'] / perf['total_trades']
                
                self._save_rules()
                break
    
    def adapt_rules(self, analytics_data: Dict):
        """根据分析数据自适应调整规则"""
        for rule in self.rules:
            perf = rule.get('performance', {})
            
            if perf.get('total_trades', 0) > 10:
                # 胜率低于40%停用
                if perf.get('win_rate', 0) < 0.4:
                    rule['active'] = False
                    rule['deactivation_reason'] = "胜率过低"
                
                # 胜率高于60%增加仓位
                elif perf.get('win_rate', 0) > 0.6:
                    rule['position_sizing']['pct_per_trade'] = min(
                        rule['position_sizing']['pct_per_trade'] * 1.2,
                        20.0
                    )
        
        self._save_rules()

def main():
    """演示"""
    print("=" * 70)
    print("📋 交易规则与策略引擎")
    print("=" * 70)
    
    engine = TradingRulesEngine()
    
    print("\n🎯 活跃规则:")
    for market in ["US", "CN", "HK"]:
        rules = engine.get_active_rules(market)
        print(f"\n{market}:")
        for rule in rules:
            perf = rule.get('performance', {})
            print(f"  • {rule['name']}: {rule['strategy_type']}")
            print(f"    胜率: {perf.get('win_rate', 0):.1%}, 交易: {perf.get('total_trades', 0)}笔")

if __name__ == "__main__":
    main()
