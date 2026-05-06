#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易信号分析SKILL v2.0
分析市场交易信号，生成买入/卖出建议
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TradingSignalAnalyzer:
    """交易信号分析器 v2.0"""
    
    # SKILL元数据
    METADATA = {
        "id": "skill_trading_signal",
        "name": "交易信号分析",
        "version": "2.0.0",
        "category": "trading",
        "description": "分析市场交易信号，生成买入/卖出建议",
        "author": "Evolution Daemon",
        "created_at": "2026-05-01T00:35:00+08:00",
        "updated_at": "2026-05-01T00:35:00+08:00",
        "enabled": True,
        "dependencies": [],
        "config": {
            "update_interval": 300,
            "max_signals": 10,
            "indicators": ["MA", "MACD", "RSI", "KDJ"],
            "timeframes": ["1d", "1w", "1m"]
        }
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.signals = []
        self.signal_history = []
        
    def initialize(self) -> bool:
        """初始化SKILL"""
        try:
            self.logger.info("初始化交易信号分析SKILL")
            # 加载历史数据
            # 初始化指标计算器
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def execute(self, market_data: Dict) -> Dict:
        """执行信号分析"""
        try:
            # 验证输入数据
            if not self.validate(market_data):
                return {"error": "输入数据验证失败"}
            
            # 计算技术指标
            indicators = self._calculate_indicators(market_data)
            
            # 生成交易信号
            signal = {
                "symbol": market_data.get("symbol", ""),
                "price": market_data.get("price", 0),
                "volume": market_data.get("volume", 0),
                "timestamp": datetime.now().isoformat(),
                "signal": self._generate_signal(market_data, indicators),
                "confidence": self._calculate_confidence(indicators),
                "indicators": indicators,
                "reason": self._generate_reason(market_data, indicators),
                "risk_level": self._assess_risk_level(market_data)
            }
            
            self.signals.append(signal)
            self.signal_history.append(signal)
            
            # 限制历史记录数量
            if len(self.signal_history) > self.config.get("max_signals", 100):
                self.signal_history = self.signal_history[-100:]
            
            return signal
            
        except Exception as e:
            self.logger.error(f"信号分析失败: {e}")
            return {"error": str(e)}
    
    def validate(self, data: Dict) -> bool:
        """验证输入数据"""
        required_fields = ["symbol", "price", "volume", "timestamp"]
        return all(field in data for field in required_fields)
    
    def get_metadata(self) -> Dict:
        """获取SKILL元数据"""
        return self.METADATA
    
    def get_status(self) -> Dict:
        """获取SKILL运行状态"""
        return {
            "status": "running",
            "signals_count": len(self.signals),
            "last_update": datetime.now().isoformat(),
            "config": self.config
        }
    
    def cleanup(self) -> bool:
        """清理SKILL资源"""
        try:
            self.signals = []
            self.signal_history = []
            return True
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
            return False
    
    def _calculate_indicators(self, data: Dict) -> Dict:
        """计算技术指标"""
        # 简化实现，实际应该使用完整的技术指标库
        price = data.get("price", 0)
        volume = data.get("volume", 0)
        change = data.get("change", 0)
        
        return {
            "MA_5": price * 1.02,
            "MA_10": price * 1.01,
            "MA_20": price * 1.00,
            "MACD": change * 0.5,
            "RSI": 50 + change * 10,
            "KDJ": 50 + change * 5,
            "volume_ratio": volume / 1000000
        }
    
    def _generate_signal(self, data: Dict, indicators: Dict) -> str:
        """生成交易信号"""
        price = data.get("price", 0)
        ma_5 = indicators.get("MA_5", price)
        ma_20 = indicators.get("MA_20", price)
        rsi = indicators.get("RSI", 50)
        
        # 综合判断
        if price > ma_5 and ma_5 > ma_20 and rsi > 50:
            return "STRONG_BUY"
        elif price > ma_5 and rsi > 50:
            return "BUY"
        elif price < ma_5 and ma_5 < ma_20 and rsi < 50:
            return "STRONG_SELL"
        elif price < ma_5 and rsi < 50:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        """计算信号置信度"""
        rsi = indicators.get("RSI", 50)
        # RSI越接近50，置信度越高
        return 1.0 - abs(rsi - 50) / 50.0 * 0.5
    
    def _generate_reason(self, data: Dict, indicators: Dict) -> str:
        """生成信号原因"""
        reasons = []
        
        price = data.get("price", 0)
        ma_5 = indicators.get("MA_5", price)
        ma_20 = indicators.get("MA_20", price)
        rsi = indicators.get("RSI", 50)
        
        if price > ma_5:
            reasons.append(f"价格{price}高于5日均线{ma_5:.2f}")
        if ma_5 > ma_20:
            reasons.append(f"5日均线{ma_5:.2f}高于20日均线{ma_20:.2f}")
        if rsi > 70:
            reasons.append(f"RSI超买({rsi:.1f})")
        elif rsi < 30:
            reasons.append(f"RSI超卖({rsi:.1f})")
        
        return "; ".join(reasons) if reasons else "技术指标中性"
    
    def _assess_risk_level(self, data: Dict) -> str:
        """评估风险等级"""
        volatility = abs(data.get("change", 0)) / data.get("price", 1) * 100
        if volatility > 5:
            return "HIGH"
        elif volatility > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_signals(self, limit: int = 10) -> List[Dict]:
        """获取最近的交易信号"""
        return self.signals[-limit:]
    
    def get_signal_history(self, days: int = 7) -> List[Dict]:
        """获取历史信号"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.signal_history if datetime.fromisoformat(s["timestamp"]) > cutoff_date]

if __name__ == "__main__":
    # 测试代码
    analyzer = TradingSignalAnalyzer()
    analyzer.initialize()
    
    test_data = {
        "symbol": "000066",
        "price": 19.82,
        "change": 0.1,
        "volume": 1000000,
        "timestamp": datetime.now().isoformat()
    }
    
    result = analyzer.execute(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== SKILL状态 ===")
    print(json.dumps(analyzer.get_status(), indent=2, ensure_ascii=False))
    
    print("\n=== SKILL元数据 ===")
    print(json.dumps(analyzer.get_metadata(), indent=2, ensure_ascii=False))
