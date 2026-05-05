#!/usr/bin/env python3
"""
A5L 故障预警系统
整合错误分类、自动修复、告警通知
"""

import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional

# 导入模块
sys.path.insert(0, '/workspace/projects/workspace/monitoring/wolverine')
from error_classifier import ErrorClassifier
from healing_executor import HealingExecutor

class FaultWarningSystem:
    """
    A5L 故障预警系统
    主控制器，整合所有组件
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.classifier = ErrorClassifier()
        self.executor = HealingExecutor(workspace)
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(f"{workspace}/logs/fault_warning.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("FaultWarning")
    
    def process_error(self, error_message: str, context: Dict = None) -> Dict:
        """
        处理错误 - 完整流程
        
        1. 分类错误
        2. 判断是否可自愈
        3. 执行修复
        4. 记录结果
        5. 发送告警（如果需要）
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "error_message": error_message[:200],
            "context": context or {},
            "classification": None,
            "healing": None,
            "alert_sent": False
        }
        
        # 步骤1: 分类错误
        self.logger.info(f"🔍 正在分类错误: {error_message[:100]}...")
        classification = self.classifier.classify(error_message, context)
        result["classification"] = classification
        
        self.logger.info(f"   分类结果: {classification['error_type']} " +
                        f"(严重性: {classification['severity']}, " +
                        f"可自愈: {classification['auto_heal']})")
        
        # 步骤2&3: 如果可自愈，执行修复
        if classification["auto_heal"]:
            self.logger.info(f"🩹 执行自动修复...")
            healing = self.executor.execute_healing(
                classification["error_type"],
                context
            )
            result["healing"] = healing
            
            if healing["success"]:
                self.logger.info(f"   ✅ 修复成功: {healing['message']}")
            else:
                self.logger.warning(f"   ❌ 修复失败: {healing['message']}")
                # 修复失败时发送告警
                result["alert_sent"] = self._send_alert(result)
        else:
            self.logger.info(f"⏭️  跳过自动修复 (auto_heal=False)")
            # 高严重性错误发送告警
            if classification["severity"] in ["critical", "high"]:
                result["alert_sent"] = self._send_alert(result)
        
        return result
    
    def _send_alert(self, result: Dict) -> bool:
        """发送告警通知"""
        try:
            # 写入告警日志
            alert_file = f"{self.workspace}/logs/alerts.json"
            alerts = []
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            
            alert = {
                "timestamp": datetime.now().isoformat(),
                "severity": result["classification"]["severity"],
                "error_type": result["classification"]["error_type"],
                "message": result["error_message"],
                "healing_attempted": result["healing"] is not None,
                "healing_success": result["healing"]["success"] if result["healing"] else False
            }
            
            alerts.append(alert)
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
            
            self.logger.warning(f"🚨 告警已记录: {alert['error_type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 告警发送失败: {e}")
            return False
    
    def get_system_health(self) -> Dict:
        """获取系统健康状态"""
        classifier_stats = self.classifier.get_statistics()
        executor_stats = self.executor.get_statistics()
        
        # 计算健康分数 (0-100)
        health_score = 100
        
        # 根据错误率扣分
        if classifier_stats["total"] > 0:
            error_rate = classifier_stats["matched"] / classifier_stats["total"]
            health_score -= int(error_rate * 20)  # 最多扣20分
        
        # 根据自愈成功率扣分
        if executor_stats["total_actions"] > 0:
            healing_failure_rate = executor_stats["failed"] / executor_stats["total_actions"]
            health_score -= int(healing_failure_rate * 30)  # 最多扣30分
        
        health_score = max(0, min(100, health_score))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "status": "healthy" if health_score > 80 else "warning" if health_score > 50 else "critical",
            "classification_stats": classifier_stats,
            "healing_stats": executor_stats
        }
    
    def generate_report(self) -> str:
        """生成系统报告"""
        health = self.get_system_health()
        
        report = f"""
# A5L 故障预警系统报告

生成时间: {health['timestamp']}

## 系统健康度

- 健康分数: {health['health_score']}/100
- 状态: {health['status']}

## 错误分类统计

- 总分类数: {health['classification_stats']['total']}
- 匹配率: {health['classification_stats']['match_rate']*100:.1f}%
- 可自愈比例: {health['classification_stats']['auto_heal_rate']*100:.1f}%

## 自愈执行统计

- 总执行: {health['healing_stats']['total_actions']}
- 成功: {health['healing_stats']['success']}
- 失败: {health['healing_stats']['failed']}
- 成功率: {health['healing_stats']['success_rate']*100:.1f}%

## 建议

"""
        if health['health_score'] < 80:
            report += "⚠️ 系统健康度低于80%，建议:\n"
            if health['classification_stats']['match_rate'] < 0.8:
                report += "- 扩充错误分类规则库\n"
            if health['healing_stats']['success_rate'] < 0.8:
                report += "- 检查自愈执行器配置\n"
        else:
            report += "✅ 系统运行正常\n"
        
        return report


# 快速测试
if __name__ == "__main__":
    print("=" * 70)
    print("🚨 A5L 故障预警系统测试")
    print("=" * 70)
    
    import os
    os.makedirs("/workspace/projects/workspace/logs", exist_ok=True)
    
    system = FaultWarningSystem()
    
    # 测试场景
    test_errors = [
        "Yahoo Finance API error: Too Many Requests - please try again later",
        "JSON parse error: Extra data: line 1 column 5 (char 4)",
        "System working normally - this is just a test"
    ]
    
    print("\n处理测试错误:\n")
    for error in test_errors:
        print(f"\n错误: {error[:60]}...")
        result = system.process_error(error)
        print(f"   分类: {result['classification']['error_type']}")
        if result['healing']:
            print(f"   修复: {'✅' if result['healing']['success'] else '❌'}")
    
    print("\n" + "=" * 70)
    print("📊 系统健康报告:")
    print("=" * 70)
    print(system.generate_report())
