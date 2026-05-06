#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 7: 监控告警系统
Monitoring & Alerting System with intelligent grading
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading

class AlertLevel(Enum):
    """告警级别"""
    P0_CRITICAL = "p0_critical"    # 立即处理
    P1_HIGH = "p1_high"            # 1小时内处理
    P2_MEDIUM = "p2_medium"        # 4小时内处理
    P3_LOW = "p3_low"              # 24小时内处理

class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """告警对象"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    component: str
    timestamp: str
    status: AlertStatus
    auto_resolve_condition: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[str] = None

class MonitoringAlertingSystem:
    """监控告警系统"""
    
    def __init__(self):
        self.alerts = []
        self.alert_counter = 0
        self.monitors = {}
        self.alert_handlers = []
        self.running = False
        
        # 告警抑制规则 (防止告警风暴)
        self.suppression_rules = {}
        self.last_alert_time = {}
        
    def register_monitor(self, name: str, check_func: Callable, interval: int):
        """
        注册监控项
        
        Args:
            name: 监控项名称
            check_func: 检查函数，返回 (是否异常, 告警级别, 消息)
            interval: 检查间隔(秒)
        """
        self.monitors[name] = {
            "check_func": check_func,
            "interval": interval,
            "last_check": None,
            "status": "ok"
        }
        print(f"✅ 监控项注册: {name} (每{interval}秒检查)")
    
    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def _generate_alert_id(self) -> str:
        """生成告警ID"""
        self.alert_counter += 1
        return f"ALERT{datetime.now().strftime('%Y%m%d%H%M%S')}{self.alert_counter:04d}"
    
    def create_alert(self, level: AlertLevel, title: str, message: str,
                    component: str, auto_resolve: Optional[str] = None) -> Alert:
        """创建告警"""
        
        # 检查抑制规则
        alert_key = f"{component}:{title}"
        now = datetime.now()
        
        if alert_key in self.last_alert_time:
            last_time = self.last_alert_time[alert_key]
            if now - last_time < timedelta(minutes=5):  # 5分钟抑制期
                print(f"   ⏸️  告警被抑制 (5分钟内重复): {title}")
                return None
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            level=level,
            title=title,
            message=message,
            component=component,
            timestamp=now.isoformat(),
            status=AlertStatus.ACTIVE,
            auto_resolve_condition=auto_resolve
        )
        
        self.alerts.append(alert)
        self.last_alert_time[alert_key] = now
        
        # 发送告警
        self._send_alert(alert)
        
        return alert
    
    def _send_alert(self, alert: Alert):
        """发送告警到所有处理器"""
        level_emoji = {
            AlertLevel.P0_CRITICAL: "🔴",
            AlertLevel.P1_HIGH: "🟠",
            AlertLevel.P2_MEDIUM: "🟡",
            AlertLevel.P3_LOW: "🔵"
        }
        
        print(f"\n{level_emoji[alert.level]} [{alert.level.value.upper()}] {alert.title}")
        print(f"   组件: {alert.component}")
        print(f"   消息: {alert.message}")
        print(f"   时间: {alert.timestamp}")
        print(f"   ID: {alert.alert_id}")
        
        # 调用外部处理器 (飞书/邮件/短信)
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"   ⚠️  告警处理器失败: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str):
        """确认告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                print(f"✅ 告警已确认: {alert_id} (by {user})")
                return True
        return False
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now().isoformat()
                print(f"✅ 告警已解决: {alert_id}")
                return True
        return False
    
    def check_auto_resolve(self):
        """检查自动恢复条件"""
        for alert in self.alerts:
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # 这里可以实现复杂的自动恢复逻辑
            # 简化版: P3级别告警1小时后自动恢复
            if alert.level == AlertLevel.P3_LOW:
                alert_time = datetime.fromisoformat(alert.timestamp)
                if datetime.now() - alert_time > timedelta(hours=1):
                    self.resolve_alert(alert.alert_id)
                    print(f"   🔄 自动恢复: {alert.title}")
    
    def run_monitoring_cycle(self):
        """执行一次监控周期"""
        for name, monitor in self.monitors.items():
            try:
                is_anomaly, level, message = monitor["check_func"]()
                
                if is_anomaly:
                    self.create_alert(
                        level=level,
                        title=f"{name} 异常",
                        message=message,
                        component=name
                    )
                    monitor["status"] = "error"
                else:
                    monitor["status"] = "ok"
                    
            except Exception as e:
                print(f"   ⚠️  监控检查失败 {name}: {e}")
    
    def get_alert_summary(self) -> Dict:
        """获取告警汇总"""
        active_alerts = [a for a in self.alerts if a.status == AlertStatus.ACTIVE]
        
        by_level = {level: 0 for level in AlertLevel}
        for alert in active_alerts:
            by_level[alert.level] += 1
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "by_level": {k.value: v for k, v in by_level.items()},
            "monitors": len(self.monitors)
        }
    
    def print_dashboard(self):
        """打印监控面板"""
        summary = self.get_alert_summary()
        
        print("\n" + "=" * 70)
        print("📊 A5L 监控告警面板")
        print("=" * 70)
        print(f"监控项: {summary['monitors']} | "
              f"总告警: {summary['total_alerts']} | "
              f"活跃告警: {summary['active_alerts']}")
        print()
        
        print("告警分布:")
        for level, count in summary['by_level'].items():
            emoji = {"p0_critical": "🔴", "p1_high": "🟠", 
                    "p2_medium": "🟡", "p3_low": "🔵"}.get(level, "⚪")
            print(f"  {emoji} {level}: {count}")
        
        if summary['active_alerts'] > 0:
            print("\n活跃告警列表:")
            for alert in self.alerts:
                if alert.status == AlertStatus.ACTIVE:
                    emoji = {"p0_critical": "🔴", "p1_high": "🟠", 
                            "p2_medium": "🟡", "p3_low": "🔵"}.get(alert.level.value, "⚪")
                    print(f"  {emoji} [{alert.level.value}] {alert.title}")
        
        print("=" * 70)


# 模拟监控检查函数
def check_trading_calendar():
    """检查交易日历"""
    from trading_calendar import TradingCalendar
    calendar = TradingCalendar()
    can_trade, reason = calendar.validate_trade()
    
    if not can_trade:
        return True, AlertLevel.P1_HIGH, f"市场休市: {reason}"
    return False, None, None

def check_data_freshness():
    """检查数据新鲜度"""
    # 模拟数据延迟检查
    delay_seconds = random.randint(0, 10)
    
    if delay_seconds > 8:
        return True, AlertLevel.P0_CRITICAL, f"数据延迟超过8秒: {delay_seconds}s"
    elif delay_seconds > 5:
        return True, AlertLevel.P2_MEDIUM, f"数据延迟: {delay_seconds}s"
    
    return False, None, None

def check_system_health():
    """检查系统健康度"""
    health_score = random.randint(85, 100)
    
    if health_score < 70:
        return True, AlertLevel.P0_CRITICAL, f"系统健康度严重下降: {health_score}"
    elif health_score < 80:
        return True, AlertLevel.P1_HIGH, f"系统健康度下降: {health_score}"
    elif health_score < 90:
        return True, AlertLevel.P3_LOW, f"系统健康度轻微下降: {health_score}"
    
    return False, None, None


def demo():
    """监控告警系统演示"""
    print("=" * 70)
    print("🚨 A5L Week 7: 监控告警系统演示")
    print("=" * 70)
    
    system = MonitoringAlertingSystem()
    
    # 注册监控项
    print("\n【注册监控项】")
    print("-" * 70)
    system.register_monitor("trading_calendar", check_trading_calendar, 60)
    system.register_monitor("data_freshness", check_data_freshness, 5)
    system.register_monitor("system_health", check_system_health, 30)
    
    # 执行监控周期
    print("\n【执行监控检查】")
    print("-" * 70)
    system.run_monitoring_cycle()
    
    # 手动创建告警演示
    print("\n【手动创建告警演示】")
    print("-" * 70)
    
    system.create_alert(
        level=AlertLevel.P0_CRITICAL,
        title="休市日交易尝试",
        message="系统在休市日尝试执行交易，已被阻止",
        component="trading_engine"
    )
    
    system.create_alert(
        level=AlertLevel.P2_MEDIUM,
        title="数据延迟",
        message="价格数据延迟超过5秒",
        component="data_pipeline"
    )
    
    system.create_alert(
        level=AlertLevel.P3_LOW,
        title="磁盘使用率",
        message="磁盘使用率达到75%",
        component="infrastructure"
    )
    
    # 告警确认演示
    print("\n【告警确认演示】")
    print("-" * 70)
    
    # 找到P2告警并确认
    for alert in system.alerts:
        if alert.level == AlertLevel.P2_MEDIUM and alert.status == AlertStatus.ACTIVE:
            system.acknowledge_alert(alert.alert_id, "COO")
            break
    
    # 显示面板
    system.print_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ 监控告警系统演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • WebSocket实时告警推送")
    print("   • 飞书/钉钉/企业微信集成")
    print("   • 告警升级策略 (未确认自动升级)")
    print("   • 智能降噪 (机器学习识别无效告警)")


if __name__ == "__main__":
    import random
    demo()
