#!/usr/bin/env python3
"""
飞书OAuth配置向导
引导用户完成OAuth授权配置
"""

import json
import os
from pathlib import Path

CONFIG_DIR = Path("/workspace/projects/workspace/config")
CONFIG_FILE = CONFIG_DIR / "feishu_oauth.json"

def setup_oauth():
    """配置OAuth"""
    print("=" * 60)
    print("🚀 A5L 飞书OAuth配置向导")
    print("=" * 60)
    print()
    
    # 检查现有配置
    existing_config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            existing_config = json.load(f)
        print("⚠️  检测到已有OAuth配置，将更新配置")
        print()
    
    print("📋 配置步骤：")
    print()
    print("1️⃣  访问飞书开放平台：https://open.feishu.cn/app")
    print("2️⃣  进入您的应用管理页面")
    print("3️⃣  在'凭证与基础信息'中获取：")
    print("   - App ID (应用ID)")
    print("   - App Secret (应用密钥)")
    print()
    print("4️⃣  在'权限管理'中添加以下权限：")
    print("   ✅ docs:document:create (创建文档)")
    print("   ✅ docs:document:read (读取文档)")
    print("   ✅ docs:document:update (更新文档)")
    print("   ✅ drive:drive:read (读取云空间)")
    print("   ✅ drive:file:read (读取文件)")
    print("   ✅ drive:file:write (写入文件)")
    print()
    print("5️⃣  发布版本（必须发布才能生效）")
    print()
    
    # 获取用户输入
    app_id = input("请输入App ID: ").strip()
    app_secret = input("请输入App Secret: ").strip()
    
    print()
    print("6️⃣  获取User Access Token：")
    print("   访问: https://open.feishu.cn/api-explorer?api=request-token&version=v3")
    print("   或执行OAuth流程获取")
    print()
    
    user_token = input("请输入User Access Token (如果有): ").strip()
    
    # 保存配置
    config = {
        "app_id": app_id,
        "app_secret": app_secret,
        "user_access_token": user_token if user_token else None,
        "token_expires_at": None,
        "refresh_token": None,
        "scope": [
            "docs:document:create",
            "docs:document:read", 
            "docs:document:update",
            "drive:drive:read",
            "drive:file:read",
            "drive:file:write"
        ]
    }
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print()
    print("✅ 配置已保存到:", CONFIG_FILE)
    print()
    
    if not user_token:
        print("⚠️  未提供User Access Token，需要执行OAuth授权流程")
        print()
        print("🔑 获取User Access Token的方法：")
        print()
        print("方法A - 使用飞书API调试台（推荐测试用）：")
        print("   1. 访问 https://open.feishu.cn/api-explorer")
        print("   2. 选择'身份验证' -> '获取 user_access_token'")
        print("   3. 填入App ID和App Secret")
        print("   4. 点击'调试'获取token")
        print("   5. 将token填入上面的配置")
        print()
        print("方法B - 使用OAuth 2.0授权流程（生产环境）：")
        print("   需要配置回调URL并引导用户授权")
        print()
    
    return config

def test_oauth():
    """测试OAuth配置"""
    print()
    print("🧪 测试OAuth配置...")
    print()
    
    if not CONFIG_FILE.exists():
        print("❌ 未找到OAuth配置，请先运行setup_oauth()")
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    user_token = config.get('user_access_token')
    
    if not user_token:
        print("❌ 未配置User Access Token")
        return False
    
    # 测试API调用
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
        
        # 测试获取用户信息
        resp = requests.get(
            'https://open.feishu.cn/open-apis/authen/v1/user_info',
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                print("✅ OAuth配置有效！")
                print(f"   用户: {data['data'].get('name', 'Unknown')}")
                return True
        
        print(f"❌ OAuth测试失败: {resp.text}")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def refresh_token():
    """刷新access token"""
    print()
    print("🔄 刷新Access Token...")
    print()
    
    if not CONFIG_FILE.exists():
        print("❌ 未找到OAuth配置")
        return None
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    app_id = config.get('app_id')
    app_secret = config.get('app_secret')
    refresh_token = config.get('refresh_token')
    
    if not all([app_id, app_secret, refresh_token]):
        print("❌ 缺少必要的凭证信息")
        return None
    
    try:
        import requests
        
        resp = requests.post(
            'https://open.feishu.cn/open-apis/authen/v1/refresh_access_token',
            json={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            },
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        data = resp.json()
        if data.get('code') == 0:
            token_data = data['data']
            
            # 更新配置
            config['user_access_token'] = token_data['access_token']
            config['refresh_token'] = token_data.get('refresh_token', refresh_token)
            config['token_expires_at'] = token_data.get('expires_in')
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ Token刷新成功！")
            return token_data['access_token']
        else:
            print(f"❌ Token刷新失败: {data.get('msg')}")
            return None
            
    except Exception as e:
        print(f"❌ 刷新异常: {e}")
        return None

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup':
            setup_oauth()
        elif sys.argv[1] == 'test':
            test_oauth()
        elif sys.argv[1] == 'refresh':
            refresh_token()
    else:
        print("用法: python3 feishu_oauth_setup.py [setup|test|refresh]")
        print()
        print("  setup  - 配置OAuth")
        print("  test   - 测试OAuth配置")
        print("  refresh - 刷新access token")
