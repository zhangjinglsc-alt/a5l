#!/usr/bin/env python3
"""
A5L 错误自动分类器
自动识别错误类型并匹配自愈规则
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional

class ErrorClassifier:
    """
    错误自动分类器
    基于模式匹配识别错误类型
    """
    
    # 错误模式定义
    ERROR_PATTERNS = {
        "yahoo_rate_limit": {
            "patterns": [
                r"Too Many Requests",
                r"rate limit exceeded",
                r"Yahoo Finance API.*limit",
                r"429.*yahoo"
            ],
            "severity": "high",
            "category": "api_limit",
            "auto_heal": True
        },
        
        "api_key_invalid": {
            "patterns": [
                r"Invalid API key",
                r"API key.*expired",
                r"authentication failed",
                r"401.*api"
            ],
            "severity": "critical",
            "category": "auth",
            "auto_heal": True
        },
        
        "position_data_corrupt": {
            "patterns": [
                r"JSON parse error",
                r"Extra data.*column",
                r"Expecting.*delimiter",
                r"Invalid JSON"
            ],
            "severity": "critical",
            "category": "data_corruption",
            "auto_heal": True
        },
        
        "feishu_doc_update_failed": {
            "patterns": [
                r"forbidden.*1770032",
                r"Tenant Token.*cannot update",
                r"non-app-created documents",
                r"permission denied.*feishu"
            ],
            "severity": "medium",
            "category": "permission",
            "auto_heal": True
        },
        
        "github_push_failed": {
            "patterns": [
                r"Push failed",
                r"Could not resolve host",
                r"Connection refused.*github",
                r"403.*push"
            ],
            "severity": "high",
            "category": "network",
            "auto_heal": True
        },
        
        "memory_error": {
            "patterns": [
                r"MemoryError",
                r"out of memory",
                r"Unable to allocate",
                r"Cannot allocate memory"
            ],
            "severity": "critical",
            "category": "resource",
            "auto_heal": True
        },
        
        "disk_full": {
            "patterns": [
                r"No space left on device",
                r"Disk quota exceeded",
                r"Write error.*disk"
            ],
            "severity": "critical",
            "category": "resource",
            "auto_heal": False
        },
        
        "network_timeout": {
            "patterns": [
                r"Connection timeout",
                r"Read timeout",
                r"Request timed out",
                r"504.*timeout"
            ],
            "severity": "medium",
            "category": "network",
            "auto_heal": True
        }
    }
    
    def __init__(self):
        self.classification_history = []
    
    def classify(self, error_message: str, context: Dict = None) -> Dict:
        """
        分类错误
        
        Args:
            error_message: 错误消息文本
            context: 上下文信息
            
        Returns:
            分类结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "error_message": error_message[:500],  # 截断长消息
            "context": context or {},
            "matched": False,
            "error_type": "unknown",
            "severity": "low",
            "category": "unknown",
            "auto_heal": False,
            "confidence": 0.0
        }
        
        # 遍历所有模式进行匹配
        for error_type, config in self.ERROR_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, error_message, re.IGNORECASE):
                    result["matched"] = True
                    result["error_type"] = error_type
                    result["severity"] = config["severity"]
                    result["category"] = config["category"]
                    result["auto_heal"] = config["auto_heal"]
                    result["confidence"] = 0.95
                    result["matched_pattern"] = pattern
                    break
            
            if result["matched"]:
                break
        
        # 记录分类历史
        self.classification_history.append(result)
        
        return result
    
    def batch_classify(self, error_messages: List[str]) -> List[Dict]:
        """批量分类错误"""
        return [self.classify(msg) for msg in error_messages]
    
    def get_statistics(self) -> Dict:
        """获取分类统计"""
        if not self.classification_history:
            return {"total": 0}
        
        total = len(self.classification_history)
        matched = len([e for e in self.classification_history if e["matched"]])
        auto_healable = len([e for e in self.classification_history if e["auto_heal"]])
        
        # 按类型统计
        type_counts = {}
        for e in self.classification_history:
            t = e["error_type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            "total": total,
            "matched": matched,
            "match_rate": matched / total if total > 0 else 0,
            "auto_healable": auto_healable,
            "auto_heal_rate": auto_healable / total if total > 0 else 0,
            "by_type": type_counts
        }
    
    def export_report(self, filepath: str):
        """导出分类报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "classifications": self.classification_history[-100:]  # 最近100条
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


# 快速测试
if __name__ == "__main__":
    print("=" * 70)
    print("🔍 A5L 错误自动分类器测试")
    print("=" * 70)
    
    classifier = ErrorClassifier()
    
    # 测试用例
    test_errors = [
        "Yahoo Finance API error: Too Many Requests",
        "JSON parse error: Extra data: line 1 column 5 (char 4)",
        "feishu API error: forbidden, code: 1770032",
        "MemoryError: Unable to allocate 5.00 GiB",
        "Push failed: Could not resolve host github.com",
        "Unknown random error that doesn't match anything"
    ]
    
    print("\n测试错误分类:\n")
    for error in test_errors:
        result = classifier.classify(error)
        status = "✅" if result["matched"] else "❓"
        auto = "🩹" if result["auto_heal"] else " "
        print(f"{status}{auto} {result['error_type']}: {error[:50]}...")
    
    print("\n" + "=" * 70)
    print("📊 分类统计:")
    stats = classifier.get_statistics()
    print(f"   总分类数: {stats['total']}")
    print(f"   匹配率: {stats['match_rate']*100:.1f}%")
    print(f"   可自愈: {stats['auto_healable']}")
    print("=" * 70)
