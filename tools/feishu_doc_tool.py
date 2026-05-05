#!/usr/bin/env python3
"""
飞书文档工具 - 直接调用OpenClaw工具
用于自动化创建飞书云文档
"""

import json
import os
import sys
from typing import Optional, Dict

def create_doc(title: str, markdown: str, folder_token: Optional[str] = None) -> Dict:
    """
    创建飞书云文档
    
    Args:
        title: 文档标题
        markdown: Markdown格式内容
        folder_token: 文件夹token（可选）
    
    Returns:
        包含doc_id, doc_url的字典
    """
    try:
        # 使用OpenClaw的feishu_create_doc工具
        # 通过调用gateway API或直接执行
        
        # 方法1: 写入临时文件并使用openclaw命令
        import tempfile
        import subprocess
        
        # 创建临时markdown文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown)
            temp_path = f.name
        
        try:
            # 构建openclaw命令
            cmd = [
                'openclaw', 'tool', 'feishu_create_doc',
                '--title', title,
                '--markdown', markdown[:50000]  # 限制大小
            ]
            
            if folder_token:
                cmd.extend(['--folder_token', folder_token])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析结果获取doc_url
                output = result.stdout
                if 'http' in output:
                    # 提取URL
                    import re
                    urls = re.findall(r'https?://[^\s<>"\']+', output)
                    if urls:
                        return {
                            'success': True,
                            'doc_url': urls[0],
                            'message': '文档创建成功'
                        }
            
            # 如果命令行方式失败，尝试直接使用API
            return _create_doc_via_api(title, markdown, folder_token)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'创建文档失败: {e}'
        }

def _create_doc_via_api(title: str, markdown: str, folder_token: Optional[str] = None) -> Dict:
    """通过飞书API直接创建文档"""
    try:
        import requests
        
        # 读取飞书配置
        config_path = '/workspace/projects/workspace/config/feishu_sync.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 获取tenant access token
        app_id = config.get('app_id', os.environ.get('FEISHU_APP_ID'))
        app_secret = config.get('app_secret', os.environ.get('FEISHU_APP_SECRET'))
        
        if not app_id or not app_secret:
            return {
                'success': False,
                'error': 'Missing Feishu credentials',
                'message': '未配置飞书API凭证'
            }
        
        # 获取token
        token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        token_resp = requests.post(token_url, json={
            'app_id': app_id,
            'app_secret': app_secret
        }, timeout=10)
        
        token_data = token_resp.json()
        if token_data.get('code') != 0:
            return {
                'success': False,
                'error': token_data.get('msg', 'Token获取失败'),
                'message': '无法获取飞书访问令牌'
            }
        
        access_token = token_data['tenant_access_token']
        
        # 创建文档
        create_url = 'https://open.feishu.cn/open-apis/docx/v1/documents'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        doc_data = {
            'title': title
        }
        
        if folder_token:
            doc_data['folder_token'] = folder_token
        
        create_resp = requests.post(create_url, headers=headers, json=doc_data, timeout=10)
        create_result = create_resp.json()
        
        if create_result.get('code') != 0:
            return {
                'success': False,
                'error': create_result.get('msg', '创建文档失败'),
                'message': 'API调用失败'
            }
        
        doc_id = create_result['data']['document']['document_id']
        doc_url = f"https://www.feishu.cn/docx/{doc_id}"
        
        # 写入内容（通过blocks API）
        # 这里简化处理，实际应该将markdown转换为飞书block格式
        # 暂时只返回文档URL，内容需要后续手动或通过其他方式添加
        
        return {
            'success': True,
            'doc_id': doc_id,
            'doc_url': doc_url,
            'message': '文档创建成功（内容需手动添加或使用网页版编辑）'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'API调用失败: {e}'
        }

def sync_markdown_to_feishu(file_path: str, title: str, folder_token: Optional[str] = None) -> Dict:
    """
    将本地markdown文件同步到飞书
    
    Args:
        file_path: 本地文件路径
        title: 文档标题
        folder_token: 文件夹token
    
    Returns:
        同步结果字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return create_doc(title, content, folder_token)
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'读取文件失败: {e}'
        }

if __name__ == '__main__':
    # 测试
    result = create_doc(
        title='测试文档',
        markdown='# 测试标题\n\n这是测试内容'
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
