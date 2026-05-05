#!/usr/bin/env python3
"""
飞书文档更新器 - 滚动更新模式
更新现有文档内容，保持URL不变
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, '/workspace/projects/workspace/tools')
from feishu_token_manager import FeishuTokenManager

CONFIG_FILE = Path("/workspace/projects/workspace/config/feishu_sync.json")


class FeishuDocUpdater:
    """飞书文档更新器 - 滚动更新模式"""
    
    def __init__(self):
        self.config = self._load_config()
        self.token_manager = FeishuTokenManager()
        self.token = self.token_manager.get_tenant_access_token()
        
    def _load_config(self) -> Dict:
        """加载配置"""
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    def update_document(self, doc_id: str, markdown_content: str) -> Dict:
        """
        更新飞书文档内容（全文替换）
        
        Args:
            doc_id: 飞书文档ID
            markdown_content: 新的Markdown内容
            
        Returns:
            更新结果
        """
        try:
            # 步骤1: 获取文档现有内容，找到第一个block
            doc_info = self._get_document_info(doc_id)
            if not doc_info['success']:
                return doc_info
            
            # 步骤2: 删除所有现有内容
            delete_result = self._delete_all_content(doc_id)
            if not delete_result['success']:
                return delete_result
            
            # 步骤3: 写入新内容
            write_result = self._write_content(doc_id, markdown_content)
            if not write_result['success']:
                return write_result
            
            return {
                'success': True,
                'doc_id': doc_id,
                'url': f"https://my.feishu.cn/docx/{doc_id}",
                'message': '文档更新成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_document_info(self, doc_id: str) -> Dict:
        """获取文档信息"""
        try:
            url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}"
            headers = {'Authorization': f'Bearer {self.token}'}
            
            resp = requests.get(url, headers=headers, timeout=30)
            result = resp.json()
            
            if result.get('code') != 0:
                return {
                    'success': False,
                    'error': result.get('msg', '获取文档信息失败')
                }
            
            return {
                'success': True,
                'document': result['data']['document']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取文档信息异常: {e}'
            }
    
    def _delete_all_content(self, doc_id: str) -> Dict:
        """删除文档所有内容（保留第一个空段落）"""
        try:
            # 获取所有blocks
            blocks_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
            headers = {'Authorization': f'Bearer {self.token}'}
            
            resp = requests.get(blocks_url, headers=headers, timeout=30)
            result = resp.json()
            
            if result.get('code') != 0:
                return {
                    'success': False,
                    'error': f'获取blocks失败: {result.get("msg")}'
                }
            
            blocks = result['data'].get('items', [])
            
            # 删除所有blocks（除了第一个）
            for block in blocks[1:]:  # 保留第一个block
                block_id = block['block_id']
                delete_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}"
                try:
                    del_resp = requests.delete(delete_url, headers=headers, timeout=30)
                    # 忽略删除失败的错误，继续删除下一个
                except:
                    pass
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': f'删除内容异常: {e}'
            }
    
    def _write_content(self, doc_id: str, markdown_content: str) -> Dict:
        """写入新内容"""
        try:
            # 将Markdown转换为blocks
            blocks = self._markdown_to_blocks(markdown_content)
            
            # 获取文档的第一个block（作为插入点）
            blocks_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
            headers = {'Authorization': f'Bearer {self.token}'}
            
            resp = requests.get(blocks_url, headers=headers, timeout=30)
            result = resp.json()
            
            if result.get('code') != 0 or not result['data'].get('items'):
                return {
                    'success': False,
                    'error': '无法获取文档block_id'
                }
            
            first_block_id = result['data']['items'][0]['block_id']
            
            # 分批写入blocks（需要在URL中指定parent_block_id）
            batch_size = 50
            for i in range(0, len(blocks), batch_size):
                batch = blocks[i:i+batch_size]
                
                # 构建children参数
                children = []
                for block in batch:
                    children.append(block)
                
                # 飞书API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
                child_url = f"{blocks_url}/{first_block_id}/children"
                
                resp = requests.post(
                    child_url,
                    headers=headers,
                    json={
                        'children': children
                    },
                    timeout=30
                )
                
                try:
                    result = resp.json()
                    if result.get('code') != 0:
                        print(f"   ⚠️ 写入blocks批次失败: {result.get('msg')}")
                except Exception as e:
                    print(f"   ⚠️ 解析响应失败: {e}")
                    print(f"      响应内容: {resp.text[:200]}")
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': f'写入内容异常: {e}'
            }
    
    def _markdown_to_blocks(self, markdown: str) -> list:
        """Markdown转飞书blocks（简化版）"""
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
            elif line.startswith('#### '):
                blocks.append({
                    'block_type': 'heading4',
                    'heading4': {'elements': [{'type': 'textRun', 'textRun': {'content': line[5:]}}]}
                })
            # 分隔线
            elif line.startswith('---') or line.startswith('==='):
                blocks.append({'block_type': 'divider', 'divider': {}})
            # 表格行（简化处理为文本）
            elif line.startswith('|') and line.endswith('|'):
                if '---' in line:
                    continue
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
            elif line[0:2].strip().isdigit() and line[1:3] == '. ':
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
    
    def update_simulation_live_status(self, market: str) -> Dict:
        """
        更新模拟交易实时状态文档
        
        Args:
            market: 'US_SIM_001', 'CN_SIM_001', or 'HK_SIM_001'
        """
        # 获取配置
        sim_config = self.config.get('layer_mapping', {}).get('simulation', {})
        live_docs = sim_config.get('live_status_docs', {})
        
        if market not in live_docs:
            return {'success': False, 'error': f'未配置{market}的文档ID'}
        
        doc_config = live_docs[market]
        doc_id = doc_config['doc_id']
        
        if doc_id == 'TO_BE_CONFIG':
            return {'success': False, 'error': f'{market}的文档ID未配置'}
        
        # 读取本地文件
        local_file = f"/workspace/projects/workspace/data/simulation/plans/{market}_LIVE_STATUS.md"
        if not os.path.exists(local_file):
            return {'success': False, 'error': f'本地文件不存在: {local_file}'}
        
        with open(local_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📝 更新 {market} 实时状态文档...")
        print(f"   文档ID: {doc_id}")
        print(f"   文档URL: {doc_config['url']}")
        
        # 更新文档
        result = self.update_document(doc_id, content)
        
        if result['success']:
            print(f"   ✅ 更新成功")
        else:
            print(f"   ❌ 更新失败: {result.get('error')}")
        
        return result


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='更新飞书文档（滚动更新模式）')
    parser.add_argument('--market', '-m', choices=['US_SIM_001', 'CN_SIM_001', 'HK_SIM_001'],
                        help='更新指定市场的实时状态')
    parser.add_argument('--all', '-a', action='store_true',
                        help='更新所有市场')
    parser.add_argument('--doc-id', '-d', help='指定文档ID')
    parser.add_argument('--file', '-f', help='要上传的本地文件')
    
    args = parser.parse_args()
    
    updater = FeishuDocUpdater()
    
    if args.all:
        print("="*70)
        print("🔄 更新所有市场实时状态文档")
        print("="*70)
        
        for market in ['US_SIM_001', 'CN_SIM_001', 'HK_SIM_001']:
            result = updater.update_simulation_live_status(market)
            print()
    
    elif args.market:
        result = updater.update_simulation_live_status(args.market)
        if result['success']:
            print(f"\n✅ 更新成功: {result['url']}")
        else:
            print(f"\n❌ 更新失败: {result.get('error')}")
    
    elif args.doc_id and args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        result = updater.update_document(args.doc_id, content)
        if result['success']:
            print(f"✅ 更新成功: {result['url']}")
        else:
            print(f"❌ 更新失败: {result.get('error')}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
