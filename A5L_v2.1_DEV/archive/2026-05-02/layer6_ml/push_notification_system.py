#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时推送系统
WebSocket服务端 + 飞书机器人通知

功能:
- WebSocket服务端 (实时行情推送)
- 信号检测与推送
- 飞书机器人集成
- 多通道通知 (价格异动、交易信号、系统告警)
"""

import asyncio
import json
import os
import sys
import websockets
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Callable
import threading
import time

sys.path.insert(0, "/workspace/projects/workspace")

# 尝试导入飞书工具
try:
    sys.path.insert(0, "/workspace/projects/workspace/TOOLS")
    from feishu_notifier import FeishuNotifier
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False

class PushNotificationSystem:
    """推送通知系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[str]] = {}  # symbol -> [client_id]
        self.price_alerts: Dict[str, Dict] = {}  # symbol -> alert config
        
        # 飞书配置
        self.feishu_webhook = os.getenv("FEISHU_WEBHOOK", "")
        
        print("📡 推送通知系统初始化")
        print(f"   WebSocket端口: 8765")
        print(f"   飞书通知: {'✅ 已配置' if self.feishu_webhook else '⚠️ 未配置'}")
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """注册客户端"""
        self.connected_clients.add(websocket)
        print(f"✅ 客户端连接，当前连接数: {len(self.connected_clients)}")
        
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
            print(f"❌ 客户端断开，当前连接数: {len(self.connected_clients)}")
    
    async def broadcast(self, message: Dict):
        """广播消息给所有客户端"""
        if not self.connected_clients:
            return
        
        message_json = json.dumps(message, ensure_ascii=False)
        
        # 发送给所有连接的客户端
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(message_json)
            except:
                disconnected.add(client)
        
        # 清理断开的客户端
        self.connected_clients -= disconnected
    
    def send_feishu_notification(self, title: str, content: str, 
                                 priority: str = "normal") -> bool:
        """
        发送飞书通知
        
        Args:
            title: 通知标题
            content: 通知内容
            priority: 优先级 (low/normal/high/critical)
            
        Returns:
            是否发送成功
        """
        if not self.feishu_webhook:
            print(f"⚠️ 飞书Webhook未配置")
            return False
        
        # 根据优先级设置颜色
        color_map = {
            "low": "grey",
            "normal": "blue",
            "high": "orange",
            "critical": "red"
        }
        color = color_map.get(priority, "blue")
        
        # 构建飞书消息卡片
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📊 {title}"
                    },
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                self.feishu_webhook,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 飞书通知发送成功: {title}")
                return True
            else:
                print(f"⚠️ 飞书通知发送失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书通知发送异常: {e}")
            return False
    
    def notify_price_alert(self, symbol: str, current_price: float,
                          alert_type: str, threshold: float):
        """
        价格异动通知
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
            alert_type: 告警类型 (up/down/volatility)
            threshold: 触发阈值
        """
        title = f"价格异动告警 - {symbol}"
        
        if alert_type == "up":
            content = f"🟢 **{symbol}** 价格突破 **{current_price:.2f}**\n上涨幅度超过 {threshold:.2%}"
            priority = "high"
        elif alert_type == "down":
            content = f"🔴 **{symbol}** 价格跌破 **{current_price:.2f}**\n下跌幅度超过 {threshold:.2%}"
            priority = "critical"
        elif alert_type == "volatility":
            content = f"🟡 **{symbol}** 波动率异常\n当前价格: {current_price:.2f}"
            priority = "normal"
        else:
            content = f"**{symbol}** 当前价格: {current_price:.2f}"
            priority = "low"
        
        # WebSocket广播 (使用后台任务)
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self.broadcast({
                "type": "price_alert",
                "symbol": symbol,
                "price": current_price,
                "alert_type": alert_type,
                "timestamp": datetime.now().isoformat()
            }))
        except RuntimeError:
            # 没有运行的事件循环，直接打印
            print(f"   [WebSocket] 价格告警: {symbol} @ {current_price}")
        
        # 飞书通知 (高优先级)
        if priority in ["high", "critical"]:
            self.send_feishu_notification(title, content, priority)
    
    def notify_trading_signal(self, symbol: str, action: str,
                             confidence: float, strategy: str):
        """
        交易信号通知
        
        Args:
            symbol: 股票代码
            action: 操作 (BUY/SELL/HOLD)
            confidence: 置信度
            strategy: 策略名称
        """
        action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(action, "⚪")
        
        title = f"交易信号 - {symbol}"
        content = f"""
{action_emoji} **操作**: {action}
📈 **标的**: {symbol}
🎯 **策略**: {strategy}
✅ **置信度**: {confidence:.1%}

请登录系统查看详情。
"""
        
        # WebSocket广播
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self.broadcast({
                "type": "trading_signal",
                "symbol": symbol,
                "action": action,
                "confidence": confidence,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }))
        except RuntimeError:
            print(f"   [WebSocket] 交易信号: {symbol} {action}")
        
        # 飞书通知
        priority = "high" if confidence > 0.8 else "normal"
        self.send_feishu_notification(title, content, priority)
    
    def notify_system_alert(self, component: str, level: str, message: str):
        """
        系统告警通知
        
        Args:
            component: 组件名称
            level: 告警级别 (INFO/WARNING/ERROR/CRITICAL)
            message: 告警消息
        """
        level_emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }.get(level, "ℹ️")
        
        title = f"系统告警 - {component}"
        content = f"""
{level_emoji} **级别**: {level}
🔧 **组件**: {component}
📝 **消息**: {message}
"""
        
        # WebSocket广播
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self.broadcast({
                "type": "system_alert",
                "component": component,
                "level": level,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }))
        except RuntimeError:
            print(f"   [WebSocket] 系统告警: [{level}] {component} - {message}")
        
        # 飞书通知 (ERROR及以上级别)
        if level in ["ERROR", "CRITICAL"]:
            priority = "critical" if level == "CRITICAL" else "high"
            self.send_feishu_notification(title, content, priority)
    
    async def start_websocket_server(self, host: str = "0.0.0.0", port: int = 8765):
        """启动WebSocket服务器"""
        print(f"🚀 启动WebSocket服务器: ws://{host}:{port}")
        
        async def handler(websocket, path):
            await self.register_client(websocket)
        
        async with websockets.serve(handler, host, port):
            print(f"✅ WebSocket服务器已启动")
            await asyncio.Future()  # 永远运行
    
    def run_async(self):
        """异步运行"""
        asyncio.run(self.start_websocket_server())
    
    def start_in_thread(self):
        """在后台线程中启动"""
        thread = threading.Thread(target=self.run_async)
        thread.daemon = True
        thread.start()
        print("🔄 WebSocket服务器已在后台线程启动")
        return thread

class NotificationDemo:
    """推送演示"""
    
    def __init__(self):
        self.push_system = PushNotificationSystem()
    
    def demo_price_alert(self):
        """价格异动演示"""
        print("\n" + "="*70)
        print("🟢 价格异动通知演示")
        print("="*70)
        
        # 模拟价格突破
        self.push_system.notify_price_alert(
            symbol="000001.SZ",
            current_price=12.50,
            alert_type="up",
            threshold=0.05
        )
        
        # 模拟价格跌破
        self.push_system.notify_price_alert(
            symbol="002594.SZ",
            current_price=245.80,
            alert_type="down",
            threshold=0.03
        )
    
    def demo_trading_signal(self):
        """交易信号演示"""
        print("\n" + "="*70)
        print("🎯 交易信号通知演示")
        print("="*70)
        
        signals = [
            ("000001.SZ", "BUY", 0.85, "Stock Wizard"),
            ("300750.SZ", "BUY", 0.92, "Trend+RS"),
            ("601318.SH", "SELL", 0.78, "Turtle Trading"),
        ]
        
        for symbol, action, confidence, strategy in signals:
            self.push_system.notify_trading_signal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy=strategy
            )
            time.sleep(0.5)
    
    def demo_system_alert(self):
        """系统告警演示"""
        print("\n" + "="*70)
        print("🚨 系统告警通知演示")
        print("="*70)
        
        alerts = [
            ("Layer 1 Data Source", "WARNING", "AKShare API响应延迟超过5秒"),
            ("Layer 2 Strategy Engine", "ERROR", "策略计算异常: turtle_trading"),
            ("Self-Healing Monitor", "INFO", "自动修复数据获取超时问题"),
        ]
        
        for component, level, message in alerts:
            self.push_system.notify_system_alert(
                component=component,
                level=level,
                message=message
            )
            time.sleep(0.5)
    
    def run(self):
        """运行演示"""
        print("="*70)
        print("📡 实时推送系统演示")
        print("="*70)
        
        self.demo_price_alert()
        self.demo_trading_signal()
        self.demo_system_alert()
        
        print("\n" + "="*70)
        print("✅ 推送系统演示完成!")
        print("="*70)
        print("\n说明:")
        print("  • WebSocket服务端: ws://localhost:8765")
        print("  • 飞书通知: 需要配置FEISHU_WEBHOOK环境变量")
        print("  • 支持3种通知类型: 价格异动、交易信号、系统告警")

def main():
    """主函数"""
    demo = NotificationDemo()
    demo.run()

if __name__ == "__main__":
    main()
