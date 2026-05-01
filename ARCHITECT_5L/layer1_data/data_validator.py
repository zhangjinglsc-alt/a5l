#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1: Data Validator
数据底座层 - 数据验证器

功能：
1. 数据完整性检查
2. 数据一致性验证
3. 异常值检测
4. 数据质量评分
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

class DataValidator:
    """数据验证器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.validation_log = f"{workspace}/data/architect_5l/validation_log.json"
        
        # 验证规则
        self.rules = self._init_validation_rules()
    
    def _init_validation_rules(self) -> Dict:
        """初始化验证规则"""
        return {
            "price": {
                "price_positive": {
                    "description": "价格必须为正数",
                    "check": lambda d: all(d.get(f, 0) > 0 for f in ['open', 'high', 'low', 'close'] if f in d),
                    "severity": "error"
                },
                "high_low_consistency": {
                    "description": "最高价 >= 最低价",
                    "check": lambda d: d.get('high', 0) >= d.get('low', 0),
                    "severity": "error"
                },
                "ohlc_consistency": {
                    "description": "最高价 >= 开盘价/收盘价 >= 最低价",
                    "check": lambda d: d.get('high', 0) >= max(d.get('open', 0), d.get('close', 0)) >= d.get('low', 0),
                    "severity": "error"
                },
                "volume_positive": {
                    "description": "成交量必须为正整数",
                    "check": lambda d: d.get('volume', 0) > 0,
                    "severity": "warning"
                },
                "change_pct_range": {
                    "description": "涨跌幅在合理范围内（-20% 到 +20%）",
                    "check": lambda d: -20 <= d.get('change_pct', 0) <= 20,
                    "severity": "warning"
                }
            },
            "financial": {
                "revenue_positive": {
                    "description": "营收必须为正",
                    "check": lambda d: d.get('revenue', 0) > 0,
                    "severity": "error"
                },
                "roe_range": {
                    "description": "ROE在合理范围内（-50% 到 +100%）",
                    "check": lambda d: -50 <= d.get('roe', 0) <= 100,
                    "severity": "warning"
                },
                "debt_ratio_range": {
                    "description": "负债率在合理范围内（0 到 100%）",
                    "check": lambda d: 0 <= d.get('debt_ratio', 0) <= 1,
                    "severity": "error"
                }
            }
        }
    
    def validate(self, data: Dict, data_type: str) -> Dict:
        """
        验证数据
        
        Args:
            data: 待验证数据
            data_type: 数据类型 (price, financial, etc.)
        
        Returns:
            验证结果
        """
        rules = self.rules.get(data_type, {})
        
        errors = []
        warnings = []
        passed = []
        
        for rule_name, rule in rules.items():
            try:
                if rule['check'](data):
                    passed.append(rule_name)
                else:
                    issue = {
                        "rule": rule_name,
                        "description": rule['description'],
                        "severity": rule['severity']
                    }
                    
                    if rule['severity'] == 'error':
                        errors.append(issue)
                    else:
                        warnings.append(issue)
            except Exception as e:
                errors.append({
                    "rule": rule_name,
                    "description": f"验证执行失败: {str(e)}",
                    "severity": "error"
                })
        
        result = {
            "valid": len(errors) == 0,
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "checks_total": len(rules),
            "checks_passed": len(passed),
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "quality_score": self._calculate_quality_score(len(errors), len(warnings), len(rules))
        }
        
        # 记录验证日志
        self._log_validation(result)
        
        return result
    
    def _calculate_quality_score(self, errors: int, warnings: int, total: int) -> float:
        """计算质量评分（0-100）"""
        if total == 0:
            return 100.0
        
        # 错误扣10分，警告扣3分
        score = 100 - errors * 10 - warnings * 3
        return max(0.0, score)
    
    def _log_validation(self, result: Dict):
        """记录验证日志"""
        logs = []
        if os.path.exists(self.validation_log):
            with open(self.validation_log, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        # 只保留最近1000条
        logs.append(result)
        logs = logs[-1000:]
        
        with open(self.validation_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def detect_outliers(self, data_series: List[float], method: str = "iqr") -> List[int]:
        """
        检测异常值
        
        Args:
            data_series: 数据序列
            method: 检测方法 (iqr, zscore)
        
        Returns:
            异常值索引列表
        """
        if len(data_series) < 4:
            return []
        
        if method == "iqr":
            return self._detect_outliers_iqr(data_series)
        elif method == "zscore":
            return self._detect_outliers_zscore(data_series)
        else:
            return []
    
    def _detect_outliers_iqr(self, data: List[float]) -> List[int]:
        """使用IQR方法检测异常值"""
        q1 = statistics.quantiles(data, n=4)[0]
        q3 = statistics.quantiles(data, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = []
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                outliers.append(i)
        
        return outliers
    
    def _detect_outliers_zscore(self, data: List[float], threshold: float = 3.0) -> List[int]:
        """使用Z-score方法检测异常值"""
        mean = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 1
        
        if std == 0:
            return []
        
        outliers = []
        for i, value in enumerate(data):
            zscore = abs((value - mean) / std)
            if zscore > threshold:
                outliers.append(i)
        
        return outliers
    
    def check_data_consistency(self, current: Dict, previous: Dict, 
                               data_type: str) -> Dict:
        """检查数据一致性"""
        issues = []
        
        if data_type == "price":
            # 检查价格跳跃
            if 'close' in current and 'close' in previous:
                price_change = abs(current['close'] - previous['close']) / previous['close'] * 100
                if price_change > 20:  # 单日涨跌超过20%
                    issues.append({
                        "type": "large_price_jump",
                        "description": f"价格大幅跳跃: {price_change:.2f}%",
                        "severity": "warning"
                    })
            
            # 检查成交量异常
            if 'volume' in current and 'volume' in previous:
                volume_change = current['volume'] / previous['volume'] if previous['volume'] > 0 else 1
                if volume_change > 10:  # 成交量放大10倍以上
                    issues.append({
                        "type": "volume_surge",
                        "description": f"成交量异常放大: {volume_change:.1f}倍",
                        "severity": "info"
                    })
        
        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_validation_summary(self, days: int = 7) -> Dict:
        """获取验证摘要"""
        if not os.path.exists(self.validation_log):
            return {"total_validations": 0, "average_quality": 0}
        
        with open(self.validation_log, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 过滤最近N天
        cutoff = datetime.now() - timedelta(days=days)
        recent_logs = [
            log for log in logs 
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        
        if not recent_logs:
            return {"total_validations": 0, "average_quality": 0}
        
        total = len(recent_logs)
        valid_count = sum(1 for log in recent_logs if log['valid'])
        avg_quality = sum(log['quality_score'] for log in recent_logs) / total
        
        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "valid_rate": valid_count / total,
            "average_quality": avg_quality,
            "total_errors": sum(log['error_count'] for log in recent_logs),
            "total_warnings": sum(log['warning_count'] for log in recent_logs)
        }
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        summary = self.get_validation_summary(days=7)
        
        report = f"""# ✅ 数据验证报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**统计周期**: 最近7天

---

## 📊 验证摘要

| 指标 | 数值 |
|------|------|
| 总验证次数 | {summary['total_validations']:,} |
| 有效数据 | {summary['valid_count']:,} ({summary.get('valid_rate', 0):.1%}) |
| 无效数据 | {summary['invalid_count']:,} |
| 平均质量分 | {summary.get('average_quality', 0):.1f}/100 |
| 总错误数 | {summary.get('total_errors', 0):,} |
| 总警告数 | {summary.get('total_warnings', 0):,} |

---

## 📋 验证规则

### 价格数据规则
- ✅ 价格必须为正数
- ✅ 最高价 >= 最低价
- ✅ 最高价 >= 开盘价/收盘价 >= 最低价
- ⚠️ 成交量必须为正整数
- ⚠️ 涨跌幅在合理范围内（-20% 到 +20%）

### 财务数据规则
- ✅ 营收必须为正
- ⚠️ ROE在合理范围内（-50% 到 +100%）
- ✅ 负债率在合理范围内（0 到 100%）

---

## 🔍 异常检测

系统使用以下方法检测异常值：
- **IQR方法**: Q1 - 1.5×IQR 到 Q3 + 1.5×IQR 之外
- **Z-Score方法**: |z-score| > 3

---

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("✅ 数据验证器 (Layer 1)")
    print("=" * 70)
    
    validator = DataValidator()
    
    # 测试数据
    print("\n🧪 测试数据验证...")
    
    # 有效数据
    valid_price = {
        "symbol": "000001.SZ",
        "date": "2026-05-02",
        "open": 10.5,
        "high": 10.8,
        "low": 10.3,
        "close": 10.6,
        "volume": 1000000,
        "change_pct": 0.95
    }
    
    result = validator.validate(valid_price, "price")
    print(f"\n✅ 有效数据测试:")
    print(f"  验证结果: {'通过' if result['valid'] else '失败'}")
    print(f"  质量评分: {result['quality_score']:.1f}")
    print(f"  错误: {result['error_count']}, 警告: {result['warning_count']}")
    
    # 无效数据
    invalid_price = {
        "symbol": "000001.SZ",
        "date": "2026-05-02",
        "open": 10.5,
        "high": 10.0,  # 错误：high < low
        "low": 10.3,
        "close": 10.6,
        "volume": -1000,  # 错误：负数
        "change_pct": 25.0  # 警告：超出范围
    }
    
    result = validator.validate(invalid_price, "price")
    print(f"\n❌ 无效数据测试:")
    print(f"  验证结果: {'通过' if result['valid'] else '失败'}")
    print(f"  质量评分: {result['quality_score']:.1f}")
    print(f"  错误: {result['error_count']}, 警告: {result['warning_count']}")
    
    if result['errors']:
        print(f"  错误详情:")
        for err in result['errors']:
            print(f"    - {err['description']}")
    
    # 异常值检测
    print("\n🔍 异常值检测...")
    data_series = [10.1, 10.2, 10.3, 10.2, 10.4, 10.5, 10.3, 10.2, 10.4, 50.0]  # 50.0是异常值
    outliers = validator.detect_outliers(data_series, method="iqr")
    print(f"  数据序列: {data_series}")
    print(f"  异常值索引: {outliers}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 验证报告:")
    report = validator.generate_validation_report()
    print(report[:500] + "...")

if __name__ == "__main__":
    main()
