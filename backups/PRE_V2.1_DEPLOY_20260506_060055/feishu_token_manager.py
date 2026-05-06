#!/usr/bin/env python3
"""
飞书Token自动刷新管理器
提供长期稳定的API访问能力
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

CONFIG_FILE = Path("/workspace/projects/workspace/config/feishu_oauth.json")


class FeishuTokenManager:
    """
    飞书Token管理器
    自动处理Token刷新，确保API调用始终有效
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.app_id = self.config.get('app_id')
        self.app_secret = self.config.get('app_secret')
        
    def _load_config(self) -> Dict:
        """加载OAuth配置"""
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(f"OAuth配置不存在: {CONFIG_FILE}")
        
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    def _save_config(self):
        """保存OAuth配置"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_tenant_access_token(self) -> Optional[str]:
        """
        获取Tenant Access Token
        这是应用级别的Token，用于操作应用有权限的资源
        
        Returns:
            有效的Tenant Access Token
        """
        # 检查现有Token是否有效
        existing_token = self.config.get('tenant_access_token')
        expires_at = self.config.get('tenant_token_expires_at')
        
        if existing_token and expires_at:
            # 提前5分钟认为过期
            if datetime.now().timestamp() < expires_at - 300:
                return existing_token
        
        # 需要刷新Token
        return self._refresh_tenant_token()
    
    def _refresh_tenant_token(self) -> Optional[str]:
        """
        刷新Tenant Access Token
        
        Returns:
            新的Tenant Access Token
        """
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            
            resp = requests.post(
                url,
                json={
                    'app_id': self.app_id,
                    'app_secret': self.app_secret
                },
                timeout=30
            )
            
            result = resp.json()
            
            if result.get('code') != 0:
                print(f"❌ 获取Tenant Token失败: {result.get('msg')}")
                return None
            
            token = result['tenant_access_token']
            expire = result.get('expire', 7200)  # 默认2小时
            
            # 更新配置
            self.config['tenant_access_token'] = token
            self.config['tenant_token_expires_at'] = datetime.now().timestamp() + expire
            self.config['tenant_token_updated_at'] = datetime.now().isoformat()
            self._save_config()
            
            print(f"✅ Tenant Token已刷新，有效期{expire//3600}小时")
            return token
            
        except Exception as e:
            print(f"❌ 刷新Tenant Token异常: {e}")
            return None
    
    def get_user_access_token(self) -> Optional[str]:
        """
        获取User Access Token
        这是用户级别的Token，用于操作用户有权限的资源
        
        注意: User Token需要用户授权，不能直接刷新
        如果配置了refresh_token，可以自动刷新
        
        Returns:
            有效的User Access Token
        """
        # 检查现有Token是否有效
        existing_token = self.config.get('user_access_token')
        expires_at = self.config.get('user_token_expires_at')
        
        if existing_token and expires_at:
            # 提前5分钟认为过期
            if datetime.now().timestamp() < expires_at - 300:
                return existing_token
        
        # 尝试使用Refresh Token刷新
        refresh_token = self.config.get('refresh_token')
        if refresh_token:
            return self._refresh_user_token(refresh_token)
        
        print("⚠️ 没有配置Refresh Token，无法自动刷新User Token")
        return None
    
    def _refresh_user_token(self, refresh_token: str) -> Optional[str]:
        """
        使用Refresh Token刷新User Access Token
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的User Access Token
        """
        try:
            url = "https://open.feishu.cn/open-apis/authen/v1/refresh_access_token"
            
            # 先获取app_access_token
            app_token = self._get_app_access_token()
            if not app_token:
                return None
            
            resp = requests.post(
                url,
                headers={'Authorization': f'Bearer {app_token}'},
                json={'grant_type': 'refresh_token', 'refresh_token': refresh_token},
                timeout=30
            )
            
            result = resp.json()
            
            if result.get('code') != 0:
                print(f"❌ 刷新User Token失败: {result.get('msg')}")
                return None
            
            data = result['data']
            access_token = data['access_token']
            refresh_token_new = data.get('refresh_token', refresh_token)
            expire = data.get('expires_in', 7200)
            
            # 更新配置
            self.config['user_access_token'] = access_token
            self.config['refresh_token'] = refresh_token_new
            self.config['user_token_expires_at'] = datetime.now().timestamp() + expire
            self.config['user_token_updated_at'] = datetime.now().isoformat()
            self._save_config()
            
            print(f"✅ User Token已刷新，有效期{expire//3600}小时")
            return access_token
            
        except Exception as e:
            print(f"❌ 刷新User Token异常: {e}")
            return None
    
    def _get_app_access_token(self) -> Optional[str]:
        """获取App Access Token"""
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
            
            resp = requests.post(
                url,
                json={
                    'app_id': self.app_id,
                    'app_secret': self.app_secret
                },
                timeout=30
            )
            
            result = resp.json()
            
            if result.get('code') != 0:
                return None
            
            return result.get('app_access_token')
            
        except Exception as e:
            print(f"❌ 获取App Token异常: {e}")
            return None
    
    def ensure_valid_token(self, token_type: str = 'tenant') -> Optional[str]:
        """
        确保获取有效的Token
        
        Args:
            token_type: 'tenant' 或 'user'
            
        Returns:
            有效的Token
        """
        if token_type == 'tenant':
            return self.get_tenant_access_token()
        elif token_type == 'user':
            return self.get_user_access_token()
        else:
            raise ValueError(f"不支持的token类型: {token_type}")


def test_token_refresh():
    """测试Token刷新"""
    print("=" * 70)
    print("🧪 测试飞书Token自动刷新")
    print("=" * 70)
    
    manager = FeishuTokenManager()
    
    # 测试Tenant Token
    print("\n1. 获取Tenant Access Token...")
    tenant_token = manager.get_tenant_access_token()
    if tenant_token:
        print(f"   ✅ 成功: {tenant_token[:20]}...")
    else:
        print("   ❌ 失败")
    
    # 测试User Token
    print("\n2. 获取User Access Token...")
    user_token = manager.get_user_access_token()
    if user_token:
        print(f"   ✅ 成功: {user_token[:20]}...")
    else:
        print("   ⚠️  未配置或已过期")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_token_refresh()
