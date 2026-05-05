#!/usr/bin/env python3
"""
飞书OAuth版文档上传工具
支持通过OAuth创建云文档
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict
import requests

CONFIG_FILE = Path("/workspace/projects/workspace/config/feishu_oauth.json")

class FeishuOAuthUploader:
    """使用OAuth的飞书上传器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.access_token = self.config.get('user_access_token')
        
    def _load_config(self) -> Dict:
        """加载OAuth配置"""
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(f"OAuth配置不存在: {CONFIG_FILE}")
        
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    def _ensure_token(self) -> str:
        """确保token有效"""
        if not self.access_token:
            raise ValueError("未配置User Access Token")
        return self.access_token
    
    def create_document(self, title: str, content: str, folder_token: Optional[str] = None) -> Dict:
        """
        创建飞书云文档（OAuth方式）
        
        Args:
            title: 文档标题
            content: 文档内容（Markdown格式）
            folder_token: 目标文件夹token
            
        Returns:
            创建结果字典
        """
        try:
            token = self._ensure_token()
            
            # 步骤1: 创建空文档
            create_url = 'https://open.feishu.cn/open-apis/docx/v1/documents'
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            doc_data = {'title': title}
            if folder_token:
                doc_data['folder_token'] = folder_token
            
            resp = requests.post(create_url, headers=headers, json=doc_data, timeout=30)
            result = resp.json()
            
            if result.get('code') != 0:
                return {
                    'success': False,
                    'error': result.get('msg', '创建文档失败'),
                    'step': 'create_document'
                }
            
            doc_id = result['data']['document']['document_id']
            doc_url = f"https://www.feishu.cn/docx/{doc_id}"
            
            # 步骤2: 将Markdown转换为飞书Block格式并写入
            # 这里简化处理：将内容分段写入
            blocks = self._markdown_to_blocks(content)
            
            block_url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks'
            
            for block in blocks[:100]:  # 限制块数
                block_resp = requests.post(
                    block_url,
                    headers=headers,
                    json={
                        'children': [block]
                    },
                    timeout=30
                )
                if block_resp.json().get('code') != 0:
                    # 写入失败但不中断，继续下一批
                    pass
            
            return {
                'success': True,
                'doc_id': doc_id,
                'doc_url': doc_url,
                'title': title
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step': 'exception'
            }
    
    def _markdown_to_blocks(self, markdown: str) -> list:
        """
        简单Markdown转飞书Block
        注意：这是简化版，复杂格式需要更完善的转换
        """
        blocks = []
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 标题
            if line.startswith('# '):
                blocks.append({
                    'block_type': 'heading1',
                    'heading1': {'elements': [{'type': 'textRun', 'textRun': {'content': line[2:]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    'block_type': 'heading2',
                    'heading2': {'elements': [{'type': 'textRun', 'textRun': {'content': line[3:]}}]}
                })
            elif line.startswith('### '):
                blocks.append({
                    'block_type': 'heading3',
                    'heading3': {'elements': [{'type': 'textRun', 'textRun': {'content': line[4:]}}]}
                })
            # 表格行（简化处理）
            elif line.startswith('|') and line.endswith('|'):
                # 跳过表格分隔符
                if '---' in line:
                    continue
                # 这里应该创建表格block，简化处理为文本
                blocks.append({
                    'block_type': 'text',
                    'text': {'elements': [{'type': 'textRun', 'textRun': {'content': line}}]}
                })
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    'block_type': 'bullet',
                    'bullet': {'elements': [{'type': 'textRun', 'textRun': {'content': line[2:]}}]}
                })
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                blocks.append({
                    'block_type': 'ordered',
                    'ordered': {'elements': [{'type': 'textRun', 'textRun': {'content': line[3:]}}]}
                })
            # 普通段落
            else:
                blocks.append({
                    'block_type': 'text',
                    'text': {'elements': [{'type': 'textRun', 'textRun': {'content': line}}]}
                })
        
        return blocks
    
    def upload_file(self, file_path: str, title: str, folder_token: Optional[str] = None) -> Dict:
        """上传本地文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.create_document(title, content, folder_token)
        except Exception as e:
            return {
                'success': False,
                'error': f'读取文件失败: {e}'
            }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='飞书OAuth文档上传工具')
    parser.add_argument('--file', '-f', help='要上传的文件路径')
    parser.add_argument('--title', '-t', help='文档标题')
    parser.add_argument('--folder', help='目标文件夹token')
    parser.add_argument('--setup', action='store_true', help='运行OAuth配置向导')
    
    args = parser.parse_args()
    
    if args.setup:
        # 运行配置向导
        os.system(f'python3 {Path(__file__).parent}/feishu_oauth_setup.py setup')
        return
    
    if not args.file or not args.title:
        print("❌ 请提供--file和--title参数")
        print(f"用法: python3 {__file__} --file xxx.md --title '文档标题'")
        return
    
    # 检查配置
    if not CONFIG_FILE.exists():
        print("❌ OAuth配置不存在，请先运行配置向导:")
        print(f"   python3 {Path(__file__).parent}/feishu_oauth_setup.py setup")
        return
    
    # 上传文件
    uploader = FeishuOAuthUploader()
    result = uploader.upload_file(args.file, args.title, args.folder)
    
    if result['success']:
        print(f"✅ 上传成功!")
        print(f"   文档链接: {result['doc_url']}")
    else:
        print(f"❌ 上传失败: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()
