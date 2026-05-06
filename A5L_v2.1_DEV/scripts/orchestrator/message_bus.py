#!/usr/bin/env python3
"""
A5L 智能体通信协议 (Message Bus)
Goal G011 Step 3

功能:
- 子系统间消息传递
- 发布订阅模式
- 点对点通信
- 消息持久化

执行时间: 2026-05-04 00:09 (冲刺模式)
"""

import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

WORKSPACE = "/workspace/projects/workspace"
MESSAGE_DB = f"{WORKSPACE}/data/message_bus.db"
LOG_FILE = f"{WORKSPACE}/logs/message_bus.log"

class MessageType(Enum):
    """消息类型"""
    TASK_REQUEST = "task_request"      # 任务请求
    TASK_RESULT = "task_result"         # 任务结果
    STATUS_UPDATE = "status_update"     # 状态更新
    ALERT = "alert"                     # 告警
    CONFIG_UPDATE = "config_update"     # 配置更新
    HEARTBEAT = "heartbeat"             # 心跳

class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self.init_db()
        self.log("="*60)
        self.log("A5L 消息总线初始化")
        self.log("="*60)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def init_db(self):
        """初始化消息数据库"""
        os.makedirs(os.path.dirname(MESSAGE_DB), exist_ok=True)
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        # 消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                sender TEXT NOT NULL,
                receiver TEXT,
                msg_type TEXT NOT NULL,
                payload TEXT,
                priority TEXT DEFAULT 'normal',
                ttl INTEGER DEFAULT 3600,
                delivered INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 订阅表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscriber TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subscriber, topic)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def publish(self, sender, msg_type, payload, topic=None, priority='normal', ttl=3600):
        """
        发布消息
        
        Args:
            sender: 发送者ID
            msg_type: 消息类型
            payload: 消息内容
            topic: 主题（用于订阅）
            priority: 优先级 (high/normal/low)
            ttl: 有效期(秒)
        """
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (id, timestamp, sender, receiver, msg_type, payload, priority, ttl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, timestamp, sender, topic, msg_type.value, json.dumps(payload), priority, ttl))
        
        conn.commit()
        conn.close()
        
        self.log(f"📤 消息发布: {msg_type.value} from {sender}")
        return msg_id
    
    def subscribe(self, subscriber, topic):
        """订阅主题"""
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO subscriptions (subscriber, topic)
                VALUES (?, ?)
            ''', (subscriber, topic))
            conn.commit()
            self.log(f"✅ 订阅成功: {subscriber} -> {topic}")
        except sqlite3.IntegrityError:
            self.log(f"ℹ️ 已订阅: {subscriber} -> {topic}")
        
        conn.close()
    
    def unsubscribe(self, subscriber, topic):
        """取消订阅"""
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM subscriptions WHERE subscriber = ? AND topic = ?
        ''', (subscriber, topic))
        
        conn.commit()
        conn.close()
        self.log(f"✅ 取消订阅: {subscriber} -> {topic}")
    
    def receive(self, subscriber, msg_type=None, limit=10):
        """
        接收消息
        
        获取订阅的主题中未读的消息
        """
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        # 获取订阅的主题
        cursor.execute('SELECT topic FROM subscriptions WHERE subscriber = ?', (subscriber,))
        topics = [row[0] for row in cursor.fetchall()]
        
        if not topics:
            conn.close()
            return []
        
        # 构建查询
        placeholders = ','.join('?' * len(topics))
        query = f'''
            SELECT id, timestamp, sender, receiver, msg_type, payload, priority
            FROM messages
            WHERE receiver IN ({placeholders})
            AND delivered = 0
        '''
        params = topics
        
        if msg_type:
            query += ' AND msg_type = ?'
            params.append(msg_type)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        
        # 标记为已送达
        msg_ids = [m[0] for m in messages]
        if msg_ids:
            placeholders = ','.join('?' * len(msg_ids))
            cursor.execute(f'''
                UPDATE messages SET delivered = 1 WHERE id IN ({placeholders})
            ''', msg_ids)
            conn.commit()
        
        conn.close()
        
        result = []
        for msg in messages:
            result.append({
                'id': msg[0],
                'timestamp': msg[1],
                'sender': msg[2],
                'topic': msg[3],
                'type': msg[4],
                'payload': json.loads(msg[5]) if msg[5] else {},
                'priority': msg[6]
            })
        
        return result
    
    def send_to(self, sender, receiver, msg_type, payload, priority='normal'):
        """
        点对点发送消息
        """
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (id, timestamp, sender, receiver, msg_type, payload, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, timestamp, sender, receiver, msg_type.value, json.dumps(payload), priority))
        
        conn.commit()
        conn.close()
        
        self.log(f"📨 点对点消息: {sender} -> {receiver} ({msg_type.value})")
        return msg_id
    
    def broadcast(self, sender, msg_type, payload, priority='normal'):
        """
        广播消息
        """
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        # 广播到特殊主题 '__all__'
        cursor.execute('''
            INSERT INTO messages (id, timestamp, sender, receiver, msg_type, payload, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, timestamp, sender, '__all__', msg_type.value, json.dumps(payload), priority))
        
        conn.commit()
        conn.close()
        
        self.log(f"📢 广播消息: {sender} -> ALL ({msg_type.value})")
        return msg_id
    
    def cleanup_expired(self):
        """清理过期消息"""
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        # 删除超过TTL的消息
        cursor.execute('''
            DELETE FROM messages
            WHERE datetime(created_at, '+' || ttl || ' seconds') < datetime('now')
        ''')
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            self.log(f"🧹 清理过期消息: {deleted} 条")
        
        return deleted
    
    def get_stats(self):
        """获取消息统计"""
        conn = sqlite3.connect(MESSAGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE delivered = 0')
        undelivered = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM subscriptions')
        total_subscriptions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'undelivered': undelivered,
            'subscriptions': total_subscriptions
        }


def main():
    """主函数 - 测试消息总线"""
    print("="*60)
    print("A5L 智能体通信协议")
    print("G011 Step 3 - 冲刺模式")
    print("="*60)
    
    bus = MessageBus()
    
    # 测试1: 订阅
    print("\n[测试1] 订阅注册")
    bus.subscribe("kg_processor", "report_new")
    bus.subscribe("signal_generator", "kg_updated")
    bus.subscribe("backup_system", "health_alert")
    
    # 测试2: 发布消息
    print("\n[测试2] 消息发布")
    bus.publish(
        sender="feishu_monitor",
        msg_type=MessageType.STATUS_UPDATE,
        payload={"event": "new_report", "filename": "test.pdf"},
        topic="report_new"
    )
    
    bus.publish(
        sender="kg_processor",
        msg_type=MessageType.STATUS_UPDATE,
        payload={"event": "entities_extracted", "count": 23},
        topic="kg_updated"
    )
    
    # 测试3: 接收消息
    print("\n[测试3] 消息接收")
    messages = bus.receive("kg_processor")
    print(f"  kg_processor 收到 {len(messages)} 条消息")
    
    messages = bus.receive("signal_generator")
    print(f"  signal_generator 收到 {len(messages)} 条消息")
    
    # 测试4: 点对点
    print("\n[测试4] 点对点通信")
    bus.send_to(
        sender="health_monitor",
        receiver="backup_system",
        msg_type=MessageType.ALERT,
        payload={"level": "warning", "message": "磁盘空间不足"}
    )
    
    # 测试5: 统计
    print("\n[测试5] 消息统计")
    stats = bus.get_stats()
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  未送达: {stats['undelivered']}")
    print(f"  订阅数: {stats['subscriptions']}")
    
    print("\n" + "="*60)
    print("✅ 消息总线测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
