#!/usr/bin/env python3
"""
A5L Feishu Real Client
飞书真实API客户端

功能:
- 获取 tenant_access_token
- 发送文本消息
- 发送富文本卡片消息
- 集成A5L通知系统

配置:
    在环境变量或 config/feishu_credentials.json 中设置:
    - FEISHU_APP_ID
    - FEISHU_APP_SECRET
    - FEISHU_CHAT_ID (默认发送群)
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('A5L.Feishu')


@dataclass
class FeishuConfig:
    """飞书配置"""
    app_id: str
    app_secret: str
    default_chat_id: Optional[str] = None


class FeishuRealClient:
    """
    飞书真实API客户端
    
    使用流程:
        1. 初始化: client = FeishuRealClient()
        2. 发送消息: client.send_text("Hello")
        3. 发送卡片: client.send_card(title="标题", content="内容")
    """
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, config: FeishuConfig = None):
        """
        初始化飞书客户端
        
        Args:
            config: 配置对象，如果为None则从文件/环境变量读取
        """
        if config is None:
            config = self._load_config()
        
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expire_time: Optional[datetime] = None
        
        logger.info(f"✅ Feishu client initialized (App: {config.app_id[:10]}...)")
    
    def _load_config(self) -> FeishuConfig:
        """加载配置"""
        # 1. 尝试从配置文件读取
        config_paths = [
            Path('/workspace/projects/workspace/config/feishu_credentials.json'),
            Path('config/feishu_credentials.json'),
            Path.home() / '.a5l' / 'feishu_credentials.json'
        ]
        
        for path in config_paths:
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    return FeishuConfig(
                        app_id=data.get('app_id') or data.get('FEISHU_APP_ID'),
                        app_secret=data.get('app_secret') or data.get('FEISHU_APP_SECRET'),
                        default_chat_id=data.get('chat_id') or data.get('FEISHU_CHAT_ID')
                    )
        
        # 2. 尝试从环境变量读取
        import os
        app_id = os.environ.get('FEISHU_APP_ID')
        app_secret = os.environ.get('FEISHU_APP_SECRET')
        chat_id = os.environ.get('FEISHU_CHAT_ID')
        
        if app_id and app_secret:
            return FeishuConfig(app_id=app_id, app_secret=app_secret, default_chat_id=chat_id)
        
        # 3. 使用硬编码配置 (用户提供的凭证)
        return FeishuConfig(
            app_id='cli_aa8a6da97fe1dcb1',
            app_secret='XfUTXgBzCbn5nQDbHDlNxeuANksXvYXd',
            default_chat_id=None  # 需要在发送时指定
        )
    
    def _get_access_token(self) -> str:
        """
        获取 tenant_access_token
        
        Returns:
            access_token
        """
        # 检查token是否过期
        if self._access_token and self._token_expire_time:
            if datetime.now() < self._token_expire_time - timedelta(minutes=5):
                return self._access_token
        
        # 获取新token
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != 0:
                raise Exception(f"Failed to get token: {result}")
            
            self._access_token = result['tenant_access_token']
            expire = result.get('expire', 7200)  # 默认2小时
            self._token_expire_time = datetime.now() + timedelta(seconds=expire)
            
            logger.info(f"✅ Token refreshed, expires in {expire}s")
            return self._access_token
            
        except Exception as e:
            logger.error(f"❌ Failed to get access token: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    # ============================================
    # 消息发送
    # ============================================
    
    def send_text(self, text: str, chat_id: str = None) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            text: 消息内容
            chat_id: 群ID，如果为None使用默认群
            
        Returns:
            API响应
        """
        chat_id = chat_id or self.config.default_chat_id
        if not chat_id:
            raise ValueError("chat_id is required (not set in config)")
        
        url = f"{self.BASE_URL}/im/v1/messages?receive_id_type=chat_id"
        headers = self._get_headers()
        
        # 消息内容 - 直接传JSON字符串
        content_json = json.dumps({"text": text})
        
        data = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": content_json
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                logger.info(f"✅ Text message sent to {chat_id[:15]}...")
                return result
            else:
                logger.error(f"❌ Failed to send text: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to send text message: {e}")
            return {"code": -1, "msg": str(e)}
    
    def send_card(self, title: str, content: str, 
                  button_text: str = None, button_url: str = None,
                  chat_id: str = None,
                  color: str = "blue") -> Dict[str, Any]:
        """
        发送卡片消息
        
        Args:
            title: 卡片标题
            content: 卡片内容
            button_text: 按钮文字(可选)
            button_url: 按钮链接(可选)
            chat_id: 群ID
            color: 颜色 (blue/green/orange/red)
            
        Returns:
            API响应
        """
        chat_id = chat_id or self.config.default_chat_id
        if not chat_id:
            raise ValueError("chat_id is required")
        
        url = f"{self.BASE_URL}/im/v1/messages?receive_id_type=chat_id"
        headers = self._get_headers()
        
        # 构建卡片内容
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content}
                }
            ]
        }
        
        # 添加按钮
        if button_text and button_url:
            card["elements"].append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": button_text},
                    "url": button_url,
                    "type": "primary"
                }]
            })
        
        # 卡片内容 - 直接传JSON字符串
        card_json = json.dumps(card)
        
        data = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": card_json
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                logger.info(f"✅ Card message sent to {chat_id[:15]}...")
                return result
            else:
                logger.error(f"❌ Failed to send card: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to send card message: {e}")
            return {"code": -1, "msg": str(e)}
    
    def send_signal_card(self, symbol: str, direction: str, strength: float,
                         reason: str = None, chat_id: str = None) -> Dict[str, Any]:
        """
        发送交易信号卡片 (A5L专用)
        
        Args:
            symbol: 股票代码
            direction: 方向 (bullish/bearish/neutral)
            strength: 信号强度 0-1
            reason: 信号理由
            chat_id: 群ID
            
        Returns:
            API响应
        """
        # 颜色根据方向
        color_map = {
            'bullish': 'red',      # 看涨用红色(中国特色)
            'bearish': 'green',    # 看跌用绿色
            'neutral': 'blue'
        }
        color = color_map.get(direction, 'blue')
        
        # 方向图标
        icon_map = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '➡️'
        }
        icon = icon_map.get(direction, '➡️')
        
        # 强度条
        strength_bar = '█' * int(strength * 10) + '░' * (10 - int(strength * 10))
        
        title = f"{icon} A5L交易信号: {symbol}"
        content = (
            f"**方向**: {direction.upper()}\n"
            f"**强度**: {strength:.0%} {strength_bar}\n"
        )
        if reason:
            content += f"\n**理由**: {reason}"
        
        return self.send_card(title, content, chat_id=chat_id, color=color)
    
    def send_decision_card(self, decision_id: str, symbol: str, action: str,
                           confidence: float, reason: str = None,
                           chat_id: str = None) -> Dict[str, Any]:
        """
        发送决策通知卡片 (A5L专用)
        
        Args:
            decision_id: 决策ID
            symbol: 股票代码
            action: 决策动作
            confidence: 置信度
            reason: 决策理由
            chat_id: 群ID
            
        Returns:
            API响应
        """
        color_map = {
            'buy': 'red',
            'sell': 'green',
            'hold': 'blue',
            'watch': 'orange'
        }
        color = color_map.get(action, 'blue')
        
        title = f"🎯 A5L决策: {symbol} {action.upper()}"
        content = f"**置信度**: {confidence:.0%}\n"
        if reason:
            content += f"\n**分析**: {reason[:100]}..."
        
        return self.send_card(title, content, chat_id=chat_id, color=color)
    
    # ============================================
    # 群管理
    # ============================================
    
    def get_chat_list(self) -> List[Dict]:
        """
        获取机器人所在的群列表
        
        Returns:
            群列表
        """
        url = f"{self.BASE_URL}/im/v1/chats"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                chats = result.get('data', {}).get('items', [])
                logger.info(f"✅ Got {len(chats)} chats")
                return chats
            else:
                logger.error(f"❌ Failed to get chats: {result}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get chat list: {e}")
            return []
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """
        获取群信息
        
        Args:
            chat_id: 群ID
            
        Returns:
            群信息
        """
        url = f"{self.BASE_URL}/im/v1/chats/{chat_id}"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                return result.get('data')
            else:
                logger.error(f"❌ Failed to get chat info: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get chat info: {e}")
            return None


# ============================================
# 便捷函数
# ============================================

_client = None

def get_feishu_client() -> FeishuRealClient:
    """获取全局飞书客户端"""
    global _client
    if _client is None:
        _client = FeishuRealClient()
    return _client


def send_text(text: str, chat_id: str = None) -> Dict:
    """便捷发送文本消息"""
    return get_feishu_client().send_text(text, chat_id)


def send_card(title: str, content: str, chat_id: str = None, **kwargs) -> Dict:
    """便捷发送卡片消息"""
    return get_feishu_client().send_card(title, content, chat_id=chat_id, **kwargs)


def send_signal(symbol: str, direction: str, strength: float, reason: str = None, chat_id: str = None) -> Dict:
    """便捷发送信号"""
    return get_feishu_client().send_signal_card(symbol, direction, strength, reason, chat_id)


def send_decision(decision_id: str, symbol: str, action: str, confidence: float, 
                  reason: str = None, chat_id: str = None) -> Dict:
    """便捷发送决策"""
    return get_feishu_client().send_decision_card(decision_id, symbol, action, confidence, reason, chat_id)


# ============================================
# 测试
# ============================================

if __name__ == '__main__':
    print("🧪 Testing A5L Feishu Real Client...")
    print("=" * 50)
    
    # 初始化客户端
    client = FeishuRealClient()
    
    # 测试1: 获取群列表
    print("\n1. 获取群列表...")
    chats = client.get_chat_list()
    print(f"   找到 {len(chats)} 个群")
    
    for chat in chats[:3]:  # 只显示前3个
        print(f"   - {chat.get('name', 'Unknown')} ({chat.get('chat_id', 'N/A')[:15]}...)")
    
    if chats:
        # 使用第一个群作为默认
        test_chat_id = chats[0]['chat_id']
        print(f"\n   使用群: {chats[0].get('name')} for testing")
        
        # 测试2: 发送文本消息
        print("\n2. 发送文本消息...")
        result = client.send_text(
            "🧪 A5L飞书客户端测试\n时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            chat_id=test_chat_id
        )
        
        if result.get('code') == 0:
            print("   ✅ 文本消息发送成功!")
        else:
            print(f"   ❌ 失败: {result.get('msg')}")
        
        # 测试3: 发送卡片消息
        print("\n3. 发送卡片消息...")
        result = client.send_card(
            title="🎯 A5L测试卡片",
            content="这是**测试内容**\n• 功能正常\n• 集成成功",
            chat_id=test_chat_id,
            color="blue"
        )
        
        if result.get('code') == 0:
            print("   ✅ 卡片消息发送成功!")
        else:
            print(f"   ❌ 失败: {result.get('msg')}")
        
        # 测试4: 发送信号卡片
        print("\n4. 发送信号卡片...")
        result = client.send_signal_card(
            symbol="000001.SZ",
            direction="bullish",
            strength=0.85,
            reason="技术面突破，MACD金叉",
            chat_id=test_chat_id
        )
        
        if result.get('code') == 0:
            print("   ✅ 信号卡片发送成功!")
        else:
            print(f"   ❌ 失败: {result.get('msg')}")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成!")
