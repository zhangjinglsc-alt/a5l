#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L3 P0: 分析偏见检测系统
提出者: Chief Oversight Officer (首席监管官)
"""
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
    """偏见检测器 - P0最高优先级"""
    
    def __init__(self):
        self.bias_checks = {}
        logger.info("👁️ Bias Detector initialized")
    
    def detect_confirmation_bias(self, analysis: Dict) -> Dict:
        """检测确认偏见"""
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
        """检测近因偏见"""
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
        """完整偏见检查"""
        results = []
        
        results.append(self.detect_confirmation_bias(analysis))
        results.append(self.detect_recency_bias(analysis))
        
        # 其他偏见检测...
        
        return results
