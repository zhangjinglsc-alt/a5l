#!/usr/bin/env python3
"""
Hermes - 统一消息协调中心 v1.0.0
A5L系统的单一消息出口

用法:
    python3 -m hermes send "消息内容" --priority P1 --source skill_name
    python3 -m hermes queue          # 查看队列
    python3 -m hermes flush          # 立即发送所有待发送
    python3 -m hermes stats          # 查看统计
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

class Priority(Enum):
    """消息优先级"""
    EMERGENCY = "P0"  # 紧急 - 立即发送
    HIGH = "P1"       # 重要 - 立即发送
    NORMAL = "P2"     # 一般 - 每小时汇总
    LOW = "P3"        # 低优先级 - 每日汇总

class Hermes:
    """Hermes消息中心 - 统一消息出口"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = Path(workspace)
        self.hermes_dir = self.workspace / "skills/hermes"
        self.queue_file = self.hermes_dir / "queue/message_queue.json"
        self.log_file = self.hermes_dir / "logs/message_log.json"
        
        # 确保目录存在
        self.hermes_dir.mkdir(parents=True, exist_ok=True)
        (self.hermes_dir / "queue").mkdir(exist_ok=True)
        (self.hermes_dir / "logs").mkdir(exist_ok=True)
        
        # 加载队列
        self.queue = self._load_queue()
    
    def _load_queue(self) -> List[Dict]:
        """加载消息队列"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_queue(self):
        """保存消息队列"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)
    
    def _log_message(self, msg: Dict):
        """记录消息到日志"""
        logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append(msg)
        
        # 只保留最近1000条
        logs = logs[-1000:]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def send(self, content: str, priority: str = "P2", source: str = "system", 
             channel: str = "auto", metadata: Optional[Dict] = None) -> str:
        """
        发送消息
        
        Args:
            content: 消息内容
            priority: 优先级 (P0/P1/P2/P3)
            source: 消息来源
            channel: 发送渠道 (auto/feishu/log)
            metadata: 附加元数据
        
        Returns:
            消息ID
        """
        msg_id = f"HERMES-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.queue):04d}"
        
        msg = {
            "id": msg_id,
            "content": content,
            "priority": priority,
            "source": source,
            "channel": channel,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "scheduled_at": None,
            "sent_at": None,
            "metadata": metadata or {}
        }
        
        # 根据优先级和时间决定发送时机
        msg["scheduled_at"] = self._schedule_time(priority)
        
        # 检查去重 (相同内容5分钟内)
        if self._is_duplicate(content):
            print(f"[Hermes] 重复消息已过滤: {content[:30]}...")
            return "DUPLICATE"
        
        # 加入队列
        self.queue.append(msg)
        self._save_queue()
        
        # P0/P1立即处理
        if priority in ["P0", "P1"]:
            self._deliver_immediately(msg)
        else:
            print(f"[Hermes] 消息已入队 [{priority}]: {content[:50]}...")
        
        return msg_id
    
    def _schedule_time(self, priority: str) -> str:
        """根据优先级和当前时间决定发送时机"""
        now = datetime.now()
        hour = now.hour
        
        # 深夜时段 (00:00-08:00)
        if hour < 8:
            if priority == "P0":
                return now.isoformat()  # 紧急不延迟
            elif priority == "P1":
                return (now.replace(hour=8, minute=30, second=0)).isoformat()
            elif priority == "P2":
                return (now.replace(hour=8, minute=30, second=0)).isoformat()
            else:  # P3
                return (now.replace(hour=9, minute=0, second=0)).isoformat()
        
        # 交易时间 (09:30-15:00)
        if 9 <= hour < 15:
            if priority in ["P0", "P1"]:
                return now.isoformat()
            elif priority == "P2":
                # 下一个整点
                next_hour = now.replace(minute=0, second=0) + timedelta(hours=1)
                return next_hour.isoformat()
            else:  # P3
                return (now.replace(hour=15, minute=30, second=0)).isoformat()
        
        # 其他时间
        return now.isoformat()
    
    def _is_duplicate(self, content: str, window_minutes: int = 5) -> bool:
        """检查是否重复消息"""
        now = datetime.now()
        
        for msg in reversed(self.queue[-20:]):  # 只检查最近20条
            if msg["content"] == content:
                msg_time = datetime.fromisoformat(msg["created_at"])
                if (now - msg_time).total_seconds() < window_minutes * 60:
                    return True
        
        return False
    
    def _deliver_immediately(self, msg: Dict):
        """立即发送消息"""
        print(f"[Hermes] 🔴 立即发送 [{msg['priority']}]: {msg['content'][:50]}...")
        
        # 这里可以集成飞书API
        # 目前先打印到控制台
        
        msg["status"] = "sent"
        msg["sent_at"] = datetime.now().isoformat()
        
        # 记录日志
        self._log_message(msg)
        
        # 从队列移除
        self.queue = [m for m in self.queue if m["id"] != msg["id"]]
        self._save_queue()
    
    def batch_send(self, messages: List[Dict]) -> List[str]:
        """批量发送 (自动合并)"""
        # 如果都是低优先级相似内容，合并为一条
        if len(messages) > 2:
            contents = [m.get("content", "") for m in messages]
            # 简单合并策略
            merged_content = f"批量通知: {len(messages)}项任务已完成"
            return [self.send(merged_content, priority="P3", source="batch")]
        
        # 否则单独发送
        ids = []
        for msg in messages:
            msg_id = self.send(
                content=msg.get("content", ""),
                priority=msg.get("priority", "P2"),
                source=msg.get("source", "batch")
            )
            ids.append(msg_id)
        
        return ids
    
    def flush_queue(self):
        """立即发送队列中所有到期的消息"""
        now = datetime.now()
        to_send = []
        to_keep = []
        
        for msg in self.queue:
            scheduled = datetime.fromisoformat(msg["scheduled_at"])
            if scheduled <= now:
                to_send.append(msg)
            else:
                to_keep.append(msg)
        
        # 按优先级排序
        to_send.sort(key=lambda m: m["priority"])
        
        # 发送
        for msg in to_send:
            self._deliver_immediately(msg)
        
        # 更新队列
        self.queue = to_keep
        self._save_queue()
        
        print(f"[Hermes] 已刷新队列: 发送{len(to_send)}条, 保留{len(to_keep)}条")
        
        return len(to_send)
    
    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        now = datetime.now()
        
        by_priority = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
        ready_to_send = 0
        
        for msg in self.queue:
            by_priority[msg["priority"]] += 1
            scheduled = datetime.fromisoformat(msg["scheduled_at"])
            if scheduled <= now:
                ready_to_send += 1
        
        return {
            "total": len(self.queue),
            "by_priority": by_priority,
            "ready_to_send": ready_to_send,
            "timestamp": now.isoformat()
        }
    
    def get_stats(self, days: int = 7) -> Dict:
        """获取消息统计"""
        if not self.log_file.exists():
            return {"error": "无日志文件"}
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 按天统计
        by_day = {}
        by_priority = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
        
        for msg in logs:
            day = msg["sent_at"][:10] if msg.get("sent_at") else msg["created_at"][:10]
            by_day[day] = by_day.get(day, 0) + 1
            by_priority[msg["priority"]] += 1
        
        return {
            "total_messages": len(logs),
            "by_priority": by_priority,
            "by_day": dict(sorted(by_day.items())[-days:]),
            "average_per_day": len(logs) // max(1, len(by_day))
        }

def main():
    hermes = Hermes()
    
    if len(sys.argv) < 2:
        print("""
Hermes - 统一消息协调中心

用法:
  python3 -m hermes send "消息" --priority P1 --source skill_name
  python3 -m hermes queue           # 查看队列
  python3 -m hermes flush           # 立即发送待发送消息
  python3 -m hermes stats           # 查看统计
        """)
        return 0
    
    command = sys.argv[1]
    
    if command == "send":
        if len(sys.argv) < 3:
            print("❌ 缺少消息内容")
            return 1
        
        content = sys.argv[2]
        priority = "P2"
        source = "cli"
        
        # 解析参数
        for i, arg in enumerate(sys.argv):
            if arg == "--priority" and i + 1 < len(sys.argv):
                priority = sys.argv[i + 1]
            if arg == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
        
        msg_id = hermes.send(content, priority=priority, source=source)
        print(f"✅ 消息已发送/入队: {msg_id}")
        return 0
    
    elif command == "queue":
        status = hermes.get_queue_status()
        print("📬 Hermes 消息队列")
        print(f"   总消息: {status['total']}")
        print(f"   优先级分布: {status['by_priority']}")
        print(f"   可发送: {status['ready_to_send']}")
        return 0
    
    elif command == "flush":
        sent = hermes.flush_queue()
        print(f"✅ 已发送 {sent} 条消息")
        return 0
    
    elif command == "stats":
        stats = hermes.get_stats()
        print("📊 Hermes 消息统计")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0
    
    else:
        print(f"❌ 未知命令: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
