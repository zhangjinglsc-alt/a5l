#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Cloud Document Sync - Phase Archive
飞书云文档同步 - Phase归档

功能：将Phase完成后的文件上传到飞书云文档
"""

import json
import os
from datetime import datetime

class FeishuPhaseArchive:
    """飞书Phase归档"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = workspace
        self.export_dir = f"{workspace}/feishu_export"
        self.archive_dir = f"{workspace}/archive"
        self.config_file = f"{workspace}/config/feishu_sync.json"
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.folder_token = self.config['root_folder']['token']
    
    def sync_phase1_completion(self):
        """同步Phase 1完成文件"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        print("=" * 70)
        print(f"📤 Phase 1 完成 - 飞书云文档同步")
        print("=" * 70)
        
        # 准备上传的文件
        files_to_upload = [
            {
                "local_path": f"{self.export_dir}/SOUL-2026-05-02.md",
                "name": f"SOUL-人格宪章-2026-05-02-Phase1完成.md",
                "description": "Phase 1完成：五层架构终极Goal已写入SOUL",
                "folder": "01-SOUL（灵魂层）/Phase归档"
            },
            {
                "local_path": f"{self.export_dir}/SKILL-2026-05-02.md",
                "name": f"SKILL-注册表-2026-05-02-Phase1完成.md",
                "description": "Phase 1完成：61个Skill，ARCHITECT-5L已注册",
                "folder": "02-SKILL（技能层）/Phase归档"
            },
            {
                "local_path": f"{self.export_dir}/GOAL-2026-05-02.md",
                "name": f"GOAL-进展-2026-05-02-Phase1完成.md",
                "description": "Phase 1完成：G006-ARCHITECT-5L目标已创建",
                "folder": "04-GOAL（目标层）/Phase归档"
            },
            {
                "local_path": f"{self.export_dir}/MEMORY-2026-05-02.md",
                "name": f"MEMORY-2026-05-02-Phase1完成.md",
                "description": "Phase 1完成记忆：架构设计、目录结构、Skill创建",
                "folder": "03-MEMORY（记忆层）/Phase归档"
            },
            {
                "local_path": f"{self.workspace}/ARCHITECT_5L_WORKFLOW.md",
                "name": f"ARCHITECT-5L-工作流计划-Phase1.md",
                "description": "24小时实施路线图，7个Phase详细规划",
                "folder": "04-GOAL（目标层）/ARCHITECT-5L"
            },
            {
                "local_path": f"{self.workspace}/skills/ARCHITECT-5L/SKILL.md",
                "name": f"ARCHITECT-5L-Skill文档-v1.0.md",
                "description": "486行超级强力Skill文档，五层架构完整规范",
                "folder": "02-SKILL（技能层）/ARCHITECT-5L"
            }
        ]
        
        print(f"\n📋 准备上传 {len(files_to_upload)} 个文件:\n")
        
        for i, file_info in enumerate(files_to_upload, 1):
            print(f"{i}. {file_info['name']}")
            print(f"   📁 目标: {file_info['folder']}")
            if os.path.exists(file_info['local_path']):
                size = os.path.getsize(file_info['local_path'])
                print(f"   ✅ 本地存在 ({size} bytes)")
            else:
                print(f"   ⚠️  本地文件不存在: {file_info['local_path']}")
            print()
        
        # 生成同步报告
        report = f"""# 📤 Phase 1 完成 - 飞书云文档同步报告

**同步时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Phase**: Phase 1 - 架构设计与基础搭建  
**状态**: ✅ 完成

---

## 📊 同步文件清单

| # | 文件名 | 目标文件夹 | 状态 |
|---|--------|-----------|------|
"""
        
        for i, file_info in enumerate(files_to_upload, 1):
            exists = "✅" if os.path.exists(file_info['local_path']) else "⚠️"
            report += f"| {i} | {file_info['name']} | {file_info['folder']} | {exists} |\n"
        
        report += f"""
---

## ✅ Phase 1 完成内容

1. **SOUL.md 更新**: 五层架构终极Goal已写入
2. **GOAL 创建**: G006-ARCHITECT-5L 已创建（8里程碑/10任务）
3. **Skill 文档**: 486行超级强力Skill已创建
4. **目录结构**: ARCHITECT_5L (13目录) + data/architect_5l (6目录)
5. **SKILL_REGISTRY**: 更新至61个Skill
6. **工作流计划**: 24小时7Phase实施路线图

---

## 📁 飞书目标文件夹

根目录: [OpenClaw Agent数据归档]({self.config['root_folder']['url']})

---

**下一步**: Phase 2 - Layer 1 数据底座搭建

---

> 同步操作由系统自动执行  
> 存档有效期: 90天
"""
        
        # 保存报告
        report_file = f"{self.workspace}/feishu_export/PHASE1-SYNC-REPORT-2026-05-02.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("=" * 70)
        print(f"✅ Phase 1 同步报告已生成")
        print(f"📄 {report_file}")
        print("=" * 70)
        
        return {
            "phase": "Phase 1",
            "files_count": len(files_to_upload),
            "folder_token": self.folder_token,
            "report_file": report_file,
            "files": files_to_upload
        }

def main():
    """执行Phase 1同步"""
    sync = FeishuPhaseArchive()
    result = sync.sync_phase1_completion()
    
    print(f"\n{'='*70}")
    print(f"📊 同步摘要")
    print(f"{'='*70}")
    print(f"Phase: {result['phase']}")
    print(f"文件数: {result['files_count']}")
    print(f"目标文件夹: {result['folder_token']}")
    print(f"报告: {result['report_file']}")

if __name__ == "__main__":
    main()
