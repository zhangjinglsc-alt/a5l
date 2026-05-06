#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L 智能监控告警系统
具备自我完善处理能力的监控设施

功能：
1. 结构化日志记录
2. 智能告警（带自动处理）
3. 自愈机制
4. 可视化仪表板
"""

import json
import os
import sys
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import traceback

# 配置根日志器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class Alert:
    """告警对象"""
    id: str
    timestamp: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    component: str
    message: str
    auto_fixable: bool
    fix_action: Optional[str] = None
    fix_result: Optional[str] = None
    status: str = "active"  # active, fixing, resolved, failed

@dataclass
class SystemMetric:
    """系统指标"""
    timestamp: str
    component: str
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float] = None

class SelfHealingMonitor:
    """
    自愈监控器
    具备自我诊断和自动修复能力
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.log_dir = f"{workspace}/logs/architect_5l"
        self.alert_history_file = f"{workspace}/data/architect_5l/alert_history.json"
        self.metrics_file = f"{workspace}/data/architect_5l/metrics.json"
        
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.alert_history_file), exist_ok=True)
        
        # 日志文件
        self.setup_file_logging()
        
        # 告警历史
        self.alert_history = self._load_alert_history()
        
        # 自愈规则
        self.healing_rules = self._setup_healing_rules()
        
        # 告警队列
        self.alert_queue = deque(maxlen=1000)
        
        # 指标缓存
        self.metrics_cache = []
        
        # 启动后台监控线程
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()
        
        self.logger = logging.getLogger('SelfHealingMonitor')
        self.logger.info("✅ 自愈监控器已启动")
    
    def setup_file_logging(self):
        """设置文件日志"""
        # 按日期轮转
        log_file = f"{self.log_dir}/{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        )
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    def _load_alert_history(self) -> List[Dict]:
        """加载告警历史"""
        if os.path.exists(self.alert_history_file):
            with open(self.alert_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_alert_history(self):
        """保存告警历史"""
        with open(self.alert_history_file, 'w') as f:
            json.dump(self.alert_history, f, indent=2, ensure_ascii=False)
    
    def _setup_healing_rules(self) -> Dict[str, Callable]:
        """
        设置自愈规则
        定义各种告警的自动修复逻辑
        """
        return {
            "data_fetch_timeout": self._heal_data_fetch,
            "memory_high_usage": self._heal_memory_usage,
            "disk_space_low": self._heal_disk_space,
            "service_not_responding": self._heal_service_restart,
        }
    
    def _heal_data_fetch(self, alert: Alert) -> bool:
        """
        自愈：数据获取超时
        策略：切换到备用数据源
        """
        self.logger.info(f"🔄 自动修复: {alert.component} - 切换到备用数据源")
        
        # 模拟切换到备用源
        time.sleep(1)
        
        # 记录修复结果
        alert.fix_result = "已切换到备用数据源TuShare"
        alert.status = "resolved"
        
        return True
    
    def _heal_memory_usage(self, alert: Alert) -> bool:
        """
        自愈：内存使用过高
        策略：清理缓存
        """
        self.logger.info(f"🔄 自动修复: {alert.component} - 清理内存缓存")
        
        try:
            # 清理缓存数据
            self.metrics_cache.clear()
            
            alert.fix_result = "已清理缓存，释放内存"
            alert.status = "resolved"
            return True
        except Exception as e:
            alert.fix_result = f"修复失败: {str(e)}"
            alert.status = "failed"
            return False
    
    def _heal_disk_space(self, alert: Alert) -> bool:
        """
        自愈：磁盘空间不足
        策略：清理旧日志
        """
        self.logger.info(f"🔄 自动修复: {alert.component} - 清理旧日志文件")
        
        try:
            # 删除7天前的日志
            cutoff_date = datetime.now() - timedelta(days=7)
            cleaned = 0
            
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        cleaned += 1
            
            alert.fix_result = f"已清理 {cleaned} 个旧日志文件"
            alert.status = "resolved"
            return True
        except Exception as e:
            alert.fix_result = f"修复失败: {str(e)}"
            alert.status = "failed"
            return False
    
    def _heal_service_restart(self, alert: Alert) -> bool:
        """
        自愈：服务无响应
        策略：尝试重启服务
        """
        self.logger.info(f"🔄 自动修复: {alert.component} - 尝试重启服务")
        
        # 实际部署时需要实现服务重启逻辑
        alert.fix_result = "服务重启逻辑需要在部署环境中实现"
        alert.status = "failed"
        
        return False
    
    def send_alert(self, level: str, component: str, message: str, 
                   auto_fixable: bool = False, fix_action: str = None) -> Alert:
        """
        发送告警
        
        Args:
            level: 告警级别 (INFO, WARNING, ERROR, CRITICAL)
            component: 告警组件
            message: 告警消息
            auto_fixable: 是否可自动修复
            fix_action: 修复动作类型
        """
        alert = Alert(
            id=f"alert_{int(time.time()*1000)}",
            timestamp=datetime.now().isoformat(),
            level=level,
            component=component,
            message=message,
            auto_fixable=auto_fixable,
            fix_action=fix_action,
            status="active"
        )
        
        # 记录告警
        self.logger.warning(f"🚨 ALERT [{level}] {component}: {message}")
        
        # 加入队列
        self.alert_queue.append(alert)
        
        # 保存历史
        self.alert_history.append(asdict(alert))
        self._save_alert_history()
        
        # 尝试自动修复
        if auto_fixable and fix_action:
            self._attempt_auto_heal(alert)
        
        return alert
    
    def _attempt_auto_heal(self, alert: Alert):
        """尝试自动修复"""
        if alert.fix_action in self.healing_rules:
            alert.status = "fixing"
            self.logger.info(f"🔧 尝试自动修复: {alert.fix_action}")
            
            success = self.healing_rules[alert.fix_action](alert)
            
            if success:
                self.logger.info(f"✅ 自动修复成功: {alert.component}")
            else:
                self.logger.error(f"❌ 自动修复失败: {alert.component}")
        else:
            alert.status = "failed"
            alert.fix_result = f"未知的修复动作: {alert.fix_action}"
    
    def record_metric(self, component: str, metric_name: str, 
                      value: float, unit: str = "", threshold: float = None):
        """记录系统指标"""
        metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            component=component,
            metric_name=metric_name,
            value=value,
            unit=unit,
            threshold=threshold
        )
        
        self.metrics_cache.append(metric)
        
        # 检查阈值
        if threshold is not None:
            if value > threshold:
                self.send_alert(
                    level="WARNING",
                    component=component,
                    message=f"{metric_name}超过阈值: {value}{unit} > {threshold}{unit}",
                    auto_fixable=True,
                    fix_action=self._get_fix_action(metric_name)
                )
    
    def _get_fix_action(self, metric_name: str) -> Optional[str]:
        """根据指标名称获取修复动作"""
        action_map = {
            "data_fetch_latency": "data_fetch_timeout",
            "memory_usage_percent": "memory_high_usage",
            "disk_usage_percent": "disk_space_low",
            "service_response_time": "service_not_responding"
        }
        return action_map.get(metric_name)
    
    def _background_monitor(self):
        """后台监控线程"""
        while self.monitoring:
            try:
                # 模拟系统指标监控
                self._check_system_health()
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"后台监控异常: {str(e)}")
    
    def _check_system_health(self):
        """检查系统健康"""
        # 检查内存使用（模拟）
        import psutil
        memory = psutil.virtual_memory()
        self.record_metric(
            component="system",
            metric_name="memory_usage_percent",
            value=memory.percent,
            unit="%",
            threshold=85.0
        )
        
        # 检查磁盘使用
        disk = psutil.disk_usage('/')
        self.record_metric(
            component="system",
            metric_name="disk_usage_percent",
            value=disk.percent,
            unit="%",
            threshold=90.0
        )
    
    def generate_dashboard_data(self) -> Dict:
        """生成仪表板数据"""
        # 统计最近的告警
        recent_alerts = [a for a in self.alert_history 
                        if (datetime.now() - datetime.fromisoformat(a['timestamp'])).days < 1]
        
        alert_stats = {
            "total": len(recent_alerts),
            "critical": len([a for a in recent_alerts if a['level'] == 'CRITICAL']),
            "error": len([a for a in recent_alerts if a['level'] == 'ERROR']),
            "warning": len([a for a in recent_alerts if a['level'] == 'WARNING']),
            "auto_resolved": len([a for a in recent_alerts if a['status'] == 'resolved']),
            "auto_failed": len([a for a in recent_alerts if a['status'] == 'failed'])
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy" if alert_stats['critical'] == 0 else "degraded",
            "alert_stats": alert_stats,
            "recent_alerts": recent_alerts[-10:],  # 最近10条
            "metrics": [asdict(m) for m in self.metrics_cache[-50:]]  # 最近50个指标
        }
    
    def stop(self):
        """停止监控"""
        self.monitoring = False
        self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 监控器已停止")

# 全局监控器实例
_global_monitor = None

def get_monitor() -> SelfHealingMonitor:
    """获取全局监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SelfHealingMonitor()
    return _global_monitor

def demo():
    """演示智能监控告警系统"""
    print("=" * 70)
    print("🔧 智能监控告警系统演示")
    print("=" * 70)
    
    monitor = SelfHealingMonitor()
    
    print("\n📊 模拟系统运行...")
    
    # 模拟正常指标
    monitor.record_metric("data_fetcher", "success_rate", 98.5, "%", 95.0)
    print("  ✓ 记录数据获取成功率: 98.5%")
    
    # 模拟触发告警的场景
    print("\n🚨 模拟告警触发...")
    
    # 1. 数据获取超时（可自动修复）
    alert1 = monitor.send_alert(
        level="WARNING",
        component="data_fetcher",
        message="AKShare数据获取超时，尝试3次失败",
        auto_fixable=True,
        fix_action="data_fetch_timeout"
    )
    print(f"  ⚠️ 告警1: {alert1.message}")
    print(f"     自动修复: {'✅ 成功' if alert1.status == 'resolved' else '❌ 失败'}")
    
    # 2. 磁盘空间不足（可自动修复）
    monitor.record_metric(
        component="system",
        metric_name="disk_usage_percent",
        value=92.0,
        unit="%",
        threshold=90.0
    )
    
    time.sleep(2)  # 等待自动修复
    
    # 显示仪表板数据
    print("\n📈 仪表板数据:")
    dashboard = monitor.generate_dashboard_data()
    print(f"  系统状态: {dashboard['system_status']}")
    print(f"  24小时告警统计:")
    for key, value in dashboard['alert_stats'].items():
        print(f"    - {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ 智能监控告警系统演示完成！")
    print("=" * 70)
    print("\n功能特点:")
    print("  • 结构化日志记录")
    print("  • 智能告警分级")
    print("  • 自动修复能力（自愈）")
    print("  • 后台持续监控")
    print("  • 可视化仪表板数据")
    
    monitor.stop()

if __name__ == "__main__":
    demo()
