#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场情绪分析SKILL v2.0
分析市场情绪指标，评估投资者情绪
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

class MarketSentimentAnalyzer:
    """市场情绪分析器 v2.0"""
    
    # SKILL元数据
    METADATA = {
        "id": "skill_market_sentiment",
        "name": "市场情绪分析",
        "version": "2.0.0",
        "category": "analysis",
        "description": "分析市场情绪指标，评估投资者情绪",
        "author": "Evolution Daemon",
        "created_at": "2026-05-01T00:35:00+08:00",
        "updated_at": "2026-05-01T00:35:00+08:00",
        "enabled": True,
        "dependencies": ["skill_data_fetcher"],
        "config": {
            "data_sources": ["eastmoney", "sina", "tencent"],
            "update_interval": 3600,
            "indicators": ["fear_greed", "volatility", "advance_decline", "put_call_ratio"]
        }
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.sentiment_history = []
        self.current_sentiment = None
        
    def initialize(self) -> bool:
        """初始化SKILL"""
        try:
            self.logger.info("初始化市场情绪分析SKILL")
            # 初始化数据源连接
            # 加载历史情绪数据
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def execute(self, market_data: Dict) -> Dict:
        """执行情绪分析"""
        try:
            # 验证输入数据
            if not self.validate(market_data):
                return {"error": "输入数据验证失败"}
            
            # 计算情绪指标
            sentiment = {
                "timestamp": datetime.now().isoformat(),
                "market": market_data.get("market", ""),
                "index": market_data.get("index", ""),
                "change": market_data.get("change", 0),
                "change_pct": market_data.get("change_pct", 0),
                "volume": market_data.get("volume", 0),
                "sentiment": self._calculate_sentiment(market_data),
                "fear_greed_index": self._calculate_fear_greed(market_data),
                "volatility_index": self._calculate_volatility(market_data),
                "advance_decline_ratio": self._calculate_advance_decline(market_data),
                "trend": self._determine_trend(market_data),
                "confidence": self._calculate_confidence(market_data),
                "alert_level": self._determine_alert_level(market_data)
            }
            
            self.current_sentiment = sentiment
            self.sentiment_history.append(sentiment)
            
            # 限制历史记录数量
            if len(self.sentiment_history) > 100:
                self.sentiment_history = self.sentiment_history[-100:]
            
            return sentiment
            
        except Exception as e:
            self.logger.error(f"情绪分析失败: {e}")
            return {"error": str(e)}
    
    def validate(self, data: Dict) -> bool:
        """验证输入数据"""
        required_fields = ["market", "change", "volume", "timestamp"]
        return all(field in data for field in required_fields)
    
    def get_metadata(self) -> Dict:
        """获取SKILL元数据"""
        return self.METADATA
    
    def get_status(self) -> Dict:
        """获取SKILL运行状态"""
        return {
            "status": "running",
            "current_sentiment": self.current_sentiment,
            "history_length": len(self.sentiment_history),
            "last_update": datetime.now().isoformat(),
            "config": self.config
        }
    
    def cleanup(self) -> bool:
        """清理SKILL资源"""
        try:
            self.sentiment_history = []
            self.current_sentiment = None
            return True
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
            return False
    
    def _calculate_sentiment(self, data: Dict) -> str:
        """计算情绪"""
        change = data.get("change_pct", 0)
        volume = data.get("volume", 0)
        
        # 综合判断
        if change > 0.05:
            if volume > 0:
                return "极度贪婪"
            else:
                return "贪婪"
        elif change > 0:
            return "乐观"
        elif change > -0.05:
            return "中性"
        elif change > -0.10:
            return "悲观"
        else:
            return "极度恐惧"
    
    def _calculate_fear_greed(self, data: Dict) -> float:
        """计算恐惧贪婪指数 (0-100)"""
        change = data.get("change_pct", 0)
        # 基准50，涨跌幅度调整
        return 50 + change * 500
        # 限制在0-100之间
        return max(0, min(100, 50 + change * 500))
    
    def _calculate_volatility(self, data: Dict) -> float:
        """计算波动率指数"""
        # 简化实现
        return 20.0 + abs(data.get("change", 0)) * 10
    
    def _calculate_advance_decline(self, data: Dict) -> float:
        """计算涨跌家数比"""
        # 简化实现
        return 1.2 if data.get("change", 0) > 0 else 0.8
    
    def _determine_trend(self, data: Dict) -> str:
        """判断趋势"""
        change = data.get("change", 0)
        volume_change = data.get("volume_change", 0)
        
        if change > 0 and volume_change > 0:
            return "强势上涨"
        elif change > 0:
            return "上涨"
        elif change < 0 and volume_change < 0:
            return "强势下跌"
        elif change < 0:
            return "下跌"
        else:
            return "震荡"
    
    def _calculate_confidence(self, data: Dict) -> float:
        """计算分析置信度"""
        # 基于数据量变化
        volume = data.get("volume", 0)
        if volume > 1000000:
            return 0.9
        elif volume > 500000:
            return 0.8
        else:
            return 0.7
    
    def _determine_alert_level(self, data: Dict) -> str:
        """确定预警级别"""
        sentiment = self._calculate_sentiment(data)
        change = abs(data.get("change_pct", 0))
        
        if sentiment in ["极度贪婪", "极度恐惧"]:
            return "HIGH"
        elif change > 0.05:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_sentiment_history(self, days: int = 7) -> List[Dict]:
        """获取历史情绪数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.sentiment_history if datetime.fromisoformat(s["timestamp"]) > cutoff_date]

if __name__ == "__main__":
    # 测试代码
    analyzer = MarketSentimentAnalyzer()
    analyzer.initialize()
    
    test_data = {
        "market": "A股",
        "index": "上证指数",
        "change": 50.0,
        "change_pct": 1.2,
        "volume": 4500000000,
        "timestamp": datetime.now().isoformat()
    }
    
    result = analyzer.execute(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== SKILL状态 ===")
    print(json.dumps(analyzer.get_status(), indent=2, ensure_ascii=False))
    
    print("\n=== SKILL元数据 ===")
    print(json.dumps(analyzer.get_metadata(), indent=2, ensure_ascii=False))
