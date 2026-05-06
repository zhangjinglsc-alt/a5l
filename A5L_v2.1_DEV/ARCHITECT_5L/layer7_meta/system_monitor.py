#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L 监控和日志系统
修复关键缺口：系统可观测性
"""

import json
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from functools import wraps

# 配置根日志器
def setup_logging(workspace: str = "/workspace/projects/workspace"):
    """设置结构化日志"""
    log_dir = f"{workspace}/logs/architect_5l"
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器 - 按日期轮转
    log_file = f"{log_dir}/{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 根日志器配置
    root_logger = logging.getLogger('architect_5l')
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# 监控装饰器
def monitor_operation(operation_name: str):
    """监控操作执行时间和成功率"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('architect_5l')
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"OPERATION_SUCCESS | {operation_name} | "
                    f"duration={duration:.3f}s | args={len(args)}"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"OPERATION_FAILED | {operation_name} | "
                    f"duration={duration:.3f}s | error={str(e)}"
                )
                raise
        
        return wrapper
    return decorator

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.logger = setup_logging(workspace)
        self.metrics_file = f"{workspace}/data/architect_5l/metrics.json"
        self.alerts = []
        
        # 监控指标
        self.metrics = {
            "system_start_time": datetime.now().isoformat(),
            "operations": {},
            "errors": [],
            "health_checks": []
        }
    
    def log_trade(self, symbol: str, action: str, shares: int, 
                  price: float, strategy: str, portfolio: str):
        """记录交易"""
        self.logger.info(
            f"TRADE_EXECUTED | symbol={symbol} | action={action} | "
            f"shares={shares} | price={price} | strategy={strategy} | "
            f"portfolio={portfolio}"
        )
    
    def log_signal(self, symbol: str, signal: str, confidence: float, 
                   sources: List[str]):
        """记录信号"""
        self.logger.info(
            f"SIGNAL_GENERATED | symbol={symbol} | signal={signal} | "
            f"confidence={confidence:.2f} | sources={','.join(sources)}"
        )
    
    def log_data_fetch(self, source: str, symbol: str, 
                       record_count: int, duration: float):
        """记录数据获取"""
        self.logger.info(
            f"DATA_FETCHED | source={source} | symbol={symbol} | "
            f"records={record_count} | duration={duration:.3f}s"
        )
    
    def log_error(self, component: str, error: str, severity: str = "error"):
        """记录错误"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error,
            "severity": severity
        }
        
        self.metrics["errors"].append(error_entry)
        
        if severity == "critical":
            self.logger.critical(f"CRITICAL_ERROR | {component} | {error}")
            self._send_alert(f"[CRITICAL] {component}: {error}")
        else:
            self.logger.error(f"ERROR | {component} | {error}")
    
    def _send_alert(self, message: str):
        """发送告警（简化版，可以接入飞书/短信）"""
        self.alerts.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        
        # 这里可以接入飞书机器人发送告警
        # feishu_bot.send_alert(message)
    
    def health_check(self) -> Dict:
        """系统健康检查"""
        checks = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # 检查数据目录
        data_dir = f"{self.workspace}/data/architect_5l"
        checks["checks"]["data_directory"] = {
            "status": "ok" if os.path.exists(data_dir) else "error",
            "path": data_dir
        }
        
        # 检查日志目录
        log_dir = f"{self.workspace}/logs/architect_5l"
        checks["checks"]["log_directory"] = {
            "status": "ok" if os.path.exists(log_dir) else "error",
            "path": log_dir
        }
        
        # 检查最近错误
        recent_errors = [
            e for e in self.metrics["errors"]
            if (datetime.now() - datetime.fromisoformat(e["timestamp"])).seconds < 3600
        ]
        
        if len(recent_errors) > 10:
            checks["checks"]["error_rate"] = {
                "status": "warning",
                "message": f"最近1小时 {len(recent_errors)} 个错误"
            }
            checks["status"] = "degraded"
        
        self.metrics["health_checks"].append(checks)
        
        return checks
    
    def generate_monitoring_report(self) -> str:
        """生成监控报告"""
        health = self.health_check()
        
        report = f"""# 📊 ARCHITECT-5L 系统监控报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**系统状态**: {"✅ 健康" if health['status'] == 'healthy' else "⚠️ 降级"}

---

## 🏥 健康检查

| 检查项 | 状态 | 详情 |
|--------|------|------|
"""
        
        for check_name, check_result in health["checks"].items():
            status_icon = "✅" if check_result["status"] == "ok" else "⚠️" if check_result["status"] == "warning" else "❌"
            report += f"| {check_name} | {status_icon} {check_result['status']} | {check_result.get('message', 'N/A')} |\n"
        
        # 错误统计
        recent_errors = len([
            e for e in self.metrics["errors"]
            if (datetime.now() - datetime.fromisoformat(e["timestamp"])).seconds < 86400
        ])
        
        report += f"""
---

## 📈 24小时统计

- **错误数**: {recent_errors}
- **系统启动**: {self.metrics['system_start_time'][:19]}
- **告警数**: {len(self.alerts)}

---

## ⚠️ 最近告警

"""
        
        if self.alerts:
            for alert in self.alerts[-5:]:
                report += f"- {alert['timestamp'][:19]}: {alert['message']}\n"
        else:
            report += "无告警\n"
        
        return report

def demo():
    """演示监控系统"""
    print("=" * 70)
    print("📊 监控系统演示")
    print("=" * 70)
    
    monitor = SystemMonitor()
    
    # 模拟一些操作日志
    print("\n📝 记录系统操作...")
    
    monitor.log_data_fetch("akshare", "000001.SZ", 30, 1.25)
    print("  ✓ 数据获取记录")
    
    monitor.log_signal("000001.SZ", "BUY", 0.85, ["stock_wizard", "trend_rs"])
    print("  ✓ 信号生成记录")
    
    monitor.log_trade("000001.SZ", "BUY", 1000, 10.5, "stock_wizard", "CN_SIM_001")
    print("  ✓ 交易执行记录")
    
    monitor.log_error("data_fetcher", "连接超时", "warning")
    print("  ✓ 错误记录")
    
    # 健康检查
    print("\n🏥 执行健康检查...")
    health = monitor.health_check()
    print(f"  系统状态: {health['status']}")
    
    # 生成报告
    print("\n📄 监控报告:")
    report = monitor.generate_monitoring_report()
    print(report)

if __name__ == "__main__":
    demo()
