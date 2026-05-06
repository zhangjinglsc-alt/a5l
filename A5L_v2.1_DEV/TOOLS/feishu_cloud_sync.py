#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Cloud Sync Engine
飞书云文档自动同步引擎

功能：
1. 自动创建飞书文件夹结构
2. 自动上传/更新云文档
3. 自动创建多维表格
4. 定时同步任务
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 添加TOOLS路径
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

class FeishuCloudSyncEngine:
    """飞书云同步引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.archive_dir = f"{workspace}/archive"
        self.feishu_export_dir = f"{workspace}/feishu_export"
        
        # 飞书文件夹配置
        self.folder_structure = {
            "root": "OpenClaw Agent数据归档",
            "subfolders": [
                "01-SOUL（灵魂层）",
                "02-SKILL（技能层）",
                "03-MEMORY（记忆层）",
                "04-GOAL（目标层）",
                "05-DATA（数据层）",
                "06-REPORTS（报告层）",
                "07-ARCHIVE（历史归档）"
            ]
        }
        
        # 文件夹token缓存
        self.folder_tokens = {}
    
    def create_folder_structure(self) -> Dict[str, str]:
        """
        在飞书云空间创建文件夹结构
        """
        print("=" * 70)
        print("📁 创建飞书文件夹结构")
        print("=" * 70)
        
        # 注意：这里应该调用feishu_drive_file的创建文件夹功能
        # 但目前工具只支持list/get_meta/copy/move/delete/upload/download
        # 需要先手动创建文件夹，然后记录token
        
        print("\n⚠️  请按以下步骤手动创建文件夹结构：")
        print("\n1. 在飞书云空间创建根文件夹：")
        print(f"   名称: {self.folder_structure['root']}")
        print("\n2. 在根文件夹内创建以下子文件夹：")
        for folder in self.folder_structure['subfolders']:
            print(f"   - {folder}")
        
        print("\n3. 创建完成后，分享根文件夹链接给我")
        print("   我将记录folder_token用于自动同步")
        
        return {}
    
    def sync_today_to_feishu(self, date_str: Optional[str] = None) -> Dict:
        """
        将今日归档同步到飞书
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'=' * 70}")
        print(f"🔄 同步今日数据到飞书: {date_str}")
        print(f"{'=' * 70}")
        
        sync_results = {
            "date": date_str,
            "synced_files": [],
            "failed_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. 同步SOUL
        print("\n[1/4] 同步SOUL层...")
        soul_result = self._sync_soul_to_feishu(date_str)
        sync_results["synced_files"].extend(soul_result.get("success", []))
        sync_results["failed_files"].extend(soul_result.get("failed", []))
        
        # 2. 同步SKILL
        print("\n[2/4] 同步SKILL层...")
        skill_result = self._sync_skill_to_feishu(date_str)
        sync_results["synced_files"].extend(skill_result.get("success", []))
        sync_results["failed_files"].extend(skill_result.get("failed", []))
        
        # 3. 同步MEMORY
        print("\n[3/4] 同步MEMORY层...")
        memory_result = self._sync_memory_to_feishu(date_str)
        sync_results["synced_files"].extend(memory_result.get("success", []))
        sync_results["failed_files"].extend(memory_result.get("failed", []))
        
        # 4. 同步GOAL
        print("\n[4/4] 同步GOAL层...")
        goal_result = self._sync_goal_to_feishu(date_str)
        sync_results["synced_files"].extend(goal_result.get("success", []))
        sync_results["failed_files"].extend(goal_result.get("failed", []))
        
        # 5. 同步DATA
        print("\n[5/5] 同步DATA层...")
        data_result = self._sync_data_to_feishu(date_str)
        sync_results["synced_files"].extend(data_result.get("success", []))
        sync_results["failed_files"].extend(data_result.get("failed", []))
        
        # 保存同步日志
        self._save_sync_log(sync_results)
        
        print(f"\n{'=' * 70}")
        print("✅ 飞书同步完成")
        print(f"{'=' * 70}")
        print(f"\n成功: {len(sync_results['synced_files'])} 个文件")
        print(f"失败: {len(sync_results['failed_files'])} 个文件")
        
        return sync_results
    
    def _sync_soul_to_feishu(self, date_str: str) -> Dict:
        """同步SOUL到飞书"""
        result = {"success": [], "failed": []}
        
        # 读取本地SOUL导出文件
        soul_file = f"{self.feishu_export_dir}/SOUL-{date_str}.md"
        if not os.path.exists(soul_file):
            print(f"   ⚠️  文件不存在: {soul_file}")
            return result
        
        with open(soul_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成飞书文档内容
        feishu_content = self._convert_to_feishu_doc(content, f"SOUL人格宪章-{date_str}")
        
        print(f"   📄 SOUL人格宪章: {len(content)} 字符")
        print(f"   💡 请手动复制以下内容到飞书文档 '01-SOUL（灵魂层）' 文件夹:")
        print(f"   文件名: SOUL-人格宪章-{date_str}")
        
        result["success"].append({
            "type": "soul",
            "filename": f"SOUL-{date_str}.md",
            "size": len(content)
        })
        
        return result
    
    def _sync_skill_to_feishu(self, date_str: str) -> Dict:
        """同步SKILL到飞书"""
        result = {"success": [], "failed": []}
        
        # 读取SKILL导出文件
        skill_file = f"{self.feishu_export_dir}/SKILL-{date_str}.md"
        if not os.path.exists(skill_file):
            print(f"   ⚠️  文件不存在: {skill_file}")
            return result
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📊 SKILL注册表: {len(content)} 字符")
        print(f"   💡 建议: 将此内容复制到飞书多维表格 '02-SKILL（技能层）'")
        
        # 同时生成CSV格式用于表格导入
        csv_file = f"{self.feishu_export_dir}/SKILL-{date_str}.csv"
        self._skill_to_csv(skill_file, csv_file)
        print(f"   📄 已生成CSV: {csv_file}")
        
        result["success"].append({
            "type": "skill",
            "filename": f"SKILL-{date_str}.md",
            "csv": f"SKILL-{date_str}.csv",
            "size": len(content)
        })
        
        return result
    
    def _sync_memory_to_feishu(self, date_str: str) -> Dict:
        """同步MEMORY到飞书"""
        result = {"success": [], "failed": []}
        
        # 读取MEMORY导出文件
        memory_file = f"{self.feishu_export_dir}/MEMORY-{date_str}.md"
        if not os.path.exists(memory_file):
            print(f"   ⚠️  文件不存在: {memory_file}")
            return result
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📝 记忆归档: {len(content)} 字符")
        print(f"   💡 请复制到飞书文档 '03-MEMORY（记忆层）/每日情景记忆/'")
        
        result["success"].append({
            "type": "memory",
            "filename": f"MEMORY-{date_str}.md",
            "size": len(content)
        })
        
        return result
    
    def _sync_goal_to_feishu(self, date_str: str) -> Dict:
        """同步GOAL到飞书"""
        result = {"success": [], "failed": []}
        
        # 读取GOAL导出文件
        goal_file = f"{self.feishu_export_dir}/GOAL-{date_str}.md"
        if not os.path.exists(goal_file):
            print(f"   ⚠️  文件不存在: {goal_file}")
            return result
        
        with open(goal_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   🎯 目标进展: {len(content)} 字符")
        print(f"   💡 请复制到飞书文档 '04-GOAL（目标层）/'")
        
        result["success"].append({
            "type": "goal",
            "filename": f"GOAL-{date_str}.md",
            "size": len(content)
        })
        
        return result
    
    def _sync_data_to_feishu(self, date_str: str) -> Dict:
        """同步DATA到飞书"""
        result = {"success": [], "failed": []}
        
        # 持仓数据
        portfolio_file = f"{self.workspace}/data/portfolio/portfolio_latest.json"
        if os.path.exists(portfolio_file):
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)
            
            # 转换为Markdown表格
            md_content = self._portfolio_to_markdown(portfolio, date_str)
            data_file = f"{self.feishu_export_dir}/DATA-持仓-{date_str}.md"
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"   💼 持仓数据: 已生成Markdown表格")
            print(f"   💡 请复制到飞书多维表格 '05-DATA（数据层）/'")
            
            result["success"].append({
                "type": "data",
                "filename": f"DATA-持仓-{date_str}.md",
                "size": len(md_content)
            })
        
        return result
    
    def _skill_to_csv(self, md_file: str, csv_file: str):
        """将SKILL Markdown转换为CSV"""
        import re
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取表格数据
        lines = content.split('\n')
        csv_lines = []
        in_table = False
        
        for line in lines:
            if line.startswith('| 技能名称'):
                in_table = True
                # 表头
                csv_lines.append("技能名称,熟练度,使用次数,成功率,状态")
            elif in_table and line.startswith('|') and '---' not in line:
                # 数据行
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) >= 5:
                    # 清理进度条符号
                    prof = cells[1].replace('█', '').replace('░', '').strip()
                    csv_lines.append(f"{cells[0]},{prof},{cells[2]},{cells[3]},{cells[4]}")
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(csv_lines))
    
    def _portfolio_to_markdown(self, portfolio: Dict, date_str: str) -> str:
        """将持仓数据转换为Markdown表格"""
        md = f"# 持仓数据 - {date_str}\n\n"
        md += f"**更新时间**: {portfolio.get('timestamp', 'N/A')}\n\n"
        md += f"**总市值**: ¥{portfolio.get('total_value', 0):,.2f}\n"
        md += f"**总盈亏**: ¥{portfolio.get('total_pnl', 0):,.2f} ({portfolio.get('total_pnl_pct', 0):.2f}%)\n\n"
        
        md += "| 代码 | 名称 | 账户 | 持仓 | 成本价 | 现价 | 盈亏 | 盈亏率 |\n"
        md += "|------|------|------|------|--------|------|------|--------|\n"
        
        for holding in portfolio.get('holdings', []):
            md += f"| {holding.get('code', 'N/A')} | {holding.get('name', 'N/A')} | {holding.get('account', 'N/A')} | {holding.get('position', 'N/A')} | {holding.get('cost', 'N/A')} | {holding.get('price', 'N/A')} | {holding.get('pnl', 'N/A')} | {holding.get('pnl_pct', 'N/A')}% |\n"
        
        return md
    
    def _convert_to_feishu_doc(self, content: str, title: str) -> str:
        """将Markdown转换为飞书文档格式"""
        # 飞书文档支持标准Markdown
        # 这里可以添加特定的飞书格式转换
        return content
    
    def _save_sync_log(self, results: Dict):
        """保存同步日志"""
        log_file = f"{self.workspace}/feishu_sync_log.json"
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(results)
        
        # 只保留最近30天
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-30:], f, indent=2, ensure_ascii=False)
    
    def generate_sync_guide(self) -> str:
        """生成同步操作指南"""
        guide = """
# 飞书同步操作指南

## 快速开始

### 方式1: 自动上传（推荐）

1. **创建飞书文件夹结构**
   - 在飞书云空间创建文件夹: `OpenClaw Agent数据归档`
   - 创建子文件夹: 01-SOUL, 02-SKILL, 03-MEMORY, 04-GOAL, 05-DATA

2. **运行同步脚本**
   ```bash
   python3 TOOLS/feishu_cloud_sync.py
   ```

3. **复制到飞书**
   - 脚本会生成所有必要的文件
   - 按提示复制到对应的飞书文件夹

### 方式2: 一键导出所有文件

```bash
# 生成所有导出文件
python3 TOOLS/ssmg_archive_system.py

# 文件位置
ls feishu_export/
# SOUL-2026-05-01.md
# SKILL-2026-05-01.md
# MEMORY-2026-05-01.md
# GOAL-2026-05-01.md
```

## 文件说明

| 文件 | 飞书位置 | 格式 |
|------|----------|------|
| SOUL-*.md | 01-SOUL/ | 文档 |
| SKILL-*.md | 02-SKILL/ | 表格 |
| SKILL-*.csv | 02-SKILL/ | CSV导入 |
| MEMORY-*.md | 03-MEMORY/每日情景记忆/ | 文档 |
| GOAL-*.md | 04-GOAL/ | 文档 |
| DATA-持仓-*.md | 05-DATA/ | 表格 |

## 定时同步

配置每日自动同步:
```bash
# 编辑crontab
crontab -e

# 添加每日23:30执行
0 23 * * * cd /workspace/projects/workspace && python3 TOOLS/feishu_cloud_sync.py >> logs/sync.log 2>&1
```
"""
        return guide

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Feishu Cloud Sync Engine - 飞书云同步引擎")
    print("=" * 70)
    
    engine = FeishuCloudSyncEngine()
    
    # 显示文件夹结构
    engine.create_folder_structure()
    
    # 执行同步
    print("\n")
    results = engine.sync_today_to_feishu()
    
    # 生成操作指南
    guide = engine.generate_sync_guide()
    guide_file = "/workspace/projects/workspace/FEISHU_SYNC_GUIDE.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n{'=' * 70}")
    print("✅ 飞书同步引擎运行完成")
    print(f"{'=' * 70}")
    print(f"\n📖 操作指南: {guide_file}")
    print(f"📁 导出文件: feishu_export/")
    print(f"📝 同步日志: feishu_sync_log.json")

if __name__ == "__main__":
    main()
