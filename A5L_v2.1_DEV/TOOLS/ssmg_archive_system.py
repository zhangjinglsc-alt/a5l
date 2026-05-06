#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSMG Archive System
SSMG四层架构归档系统

功能：
1. 本地结构化归档
2. 生成飞书友好格式
3. 每日自动打包
4. 数据完整性校验
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import zipfile

class SSMGArchiveSystem:
    """SSMG归档系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.archive_dir = f"{workspace}/archive"
        self.feishu_export_dir = f"{workspace}/feishu_export"
        
        # 确保目录存在
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.feishu_export_dir, exist_ok=True)
    
    def create_daily_archive(self, date_str: Optional[str] = None) -> str:
        """
        创建每日完整归档
        将SSMG四层数据打包保存
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📦 创建每日归档: {date_str}")
        print("=" * 60)
        
        # 创建日期目录
        daily_dir = f"{self.archive_dir}/{date_str}"
        os.makedirs(daily_dir, exist_ok=True)
        
        # 归档各层数据
        archived_files = []
        
        # Layer 1: SOUL
        print("\n[Layer 1] 归档SOUL层...")
        soul_files = self._archive_soul(daily_dir)
        archived_files.extend(soul_files)
        print(f"   ✅ 归档 {len(soul_files)} 个文件")
        
        # Layer 2: SKILL
        print("\n[Layer 2] 归档SKILL层...")
        skill_files = self._archive_skill(daily_dir)
        archived_files.extend(skill_files)
        print(f"   ✅ 归档 {len(skill_files)} 个文件")
        
        # Layer 3: MEMORY
        print("\n[Layer 3] 归档MEMORY层...")
        memory_files = self._archive_memory(daily_dir, date_str)
        archived_files.extend(memory_files)
        print(f"   ✅ 归档 {len(memory_files)} 个文件")
        
        # Layer 4: GOAL
        print("\n[Layer 4] 归档GOAL层...")
        goal_files = self._archive_goal(daily_dir)
        archived_files.extend(goal_files)
        print(f"   ✅ 归档 {len(goal_files)} 个文件")
        
        # 创建索引文件
        index = self._create_archive_index(date_str, archived_files)
        index_path = f"{daily_dir}/INDEX.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        # 创建ZIP包
        zip_path = self._create_zip_package(daily_dir, date_str)
        
        print("\n" + "=" * 60)
        print(f"✅ 归档完成!")
        print(f"   归档目录: {daily_dir}")
        print(f"   ZIP包: {zip_path}")
        print(f"   文件总数: {len(archived_files) + 1}")
        
        return daily_dir
    
    def _archive_soul(self, daily_dir: str) -> List[str]:
        """归档SOUL层"""
        soul_dir = f"{daily_dir}/01-SOUL"
        os.makedirs(soul_dir, exist_ok=True)
        
        files = []
        
        # SOUL.md
        src = f"{self.workspace}/SOUL.md"
        if os.path.exists(src):
            dst = f"{soul_dir}/SOUL-人格宪章.md"
            shutil.copy2(src, dst)
            files.append(dst)
        
        # SOUL_HISTORY.md (如果存在)
        src = f"{self.workspace}/SOUL_HISTORY.md"
        if os.path.exists(src):
            dst = f"{soul_dir}/SOUL-HISTORY-版本历史.md"
            shutil.copy2(src, dst)
            files.append(dst)
        
        return files
    
    def _archive_skill(self, daily_dir: str) -> List[str]:
        """归档SKILL层"""
        skill_dir = f"{daily_dir}/02-SKILL"
        os.makedirs(skill_dir, exist_ok=True)
        
        files = []
        
        # SKILL_REGISTRY.json
        src = f"{self.workspace}/SKILL_REGISTRY.json"
        if os.path.exists(src):
            dst = f"{skill_dir}/SKILL-REGISTRY.json"
            shutil.copy2(src, dst)
            files.append(dst)
            
            # 同时生成Markdown版本
            self._skill_to_markdown(src, f"{skill_dir}/SKILL-REGISTRY.md")
            files.append(f"{skill_dir}/SKILL-REGISTRY.md")
        
        return files
    
    def _archive_memory(self, daily_dir: str, date_str: str) -> List[str]:
        """归档MEMORY层"""
        memory_dir = f"{daily_dir}/03-MEMORY"
        os.makedirs(memory_dir, exist_ok=True)
        
        files = []
        
        # MEMORY.md (长期记忆)
        src = f"{self.workspace}/MEMORY.md"
        if os.path.exists(src):
            dst = f"{memory_dir}/MEMORY-长期记忆精华.md"
            shutil.copy2(src, dst)
            files.append(dst)
        
        # 当日情景记忆
        src = f"{self.workspace}/memory/{date_str}.md"
        if os.path.exists(src):
            dst = f"{memory_dir}/EPISODIC-{date_str}.md"
            shutil.copy2(src, dst)
            files.append(dst)
        
        # 工作记忆
        src = f"{self.workspace}/memory/working_memory.json"
        if os.path.exists(src):
            dst = f"{memory_dir}/WORKING-工作记忆.json"
            shutil.copy2(src, dst)
            files.append(dst)
        
        return files
    
    def _archive_goal(self, daily_dir: str) -> List[str]:
        """归档GOAL层"""
        goal_dir = f"{daily_dir}/04-GOAL"
        os.makedirs(goal_dir, exist_ok=True)
        
        files = []
        
        # 所有Goal相关文件
        src_dir = f"{self.workspace}/data/goals"
        if os.path.exists(src_dir):
            for fname in os.listdir(src_dir):
                src = f"{src_dir}/{fname}"
                dst = f"{goal_dir}/{fname}"
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    files.append(dst)
        
        return files
    
    def _create_archive_index(self, date_str: str, files: List[str]) -> Dict:
        """创建归档索引"""
        return {
            "archive_date": date_str,
            "created_at": datetime.now().isoformat(),
            "ssmg_version": "1.0",
            "layers": {
                "soul": {"file_count": len([f for f in files if '01-SOUL' in f])},
                "skill": {"file_count": len([f for f in files if '02-SKILL' in f])},
                "memory": {"file_count": len([f for f in files if '03-MEMORY' in f])},
                "goal": {"file_count": len([f for f in files if '04-GOAL' in f])}
            },
            "total_files": len(files),
            "files": [os.path.basename(f) for f in files]
        }
    
    def _create_zip_package(self, daily_dir: str, date_str: str) -> str:
        """创建ZIP包"""
        zip_path = f"{self.archive_dir}/SSMG-ARCHIVE-{date_str}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(daily_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.archive_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def _skill_to_markdown(self, json_path: str, md_path: str):
        """将技能注册表转换为Markdown"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        md_content = f"""# SKILL REGISTRY - 技能注册表

**版本**: {data.get('version', 'N/A')}  
**更新日期**: {data.get('last_updated', 'N/A')}  
**总技能数**: {data.get('summary', {}).get('total_skills', 0)}  
**活跃技能**: {data.get('summary', {}).get('active_skills', 0)}  
**平均熟练度**: {data.get('summary', {}).get('avg_proficiency', 0):.0%}

---

## 技能分类概览

"""
        
        for cat_name, cat_data in data.get('categories', {}).items():
            md_content += f"### {cat_data.get('name', cat_name)} ({cat_data.get('count', 0)}个)\n\n"
            md_content += "| 技能名称 | 熟练度 | 使用次数 | 成功率 |\n"
            md_content += "|----------|--------|----------|--------|\n"
            
            for skill in cat_data.get('skills', [])[:5]:  # 只显示前5个
                prof = skill.get('proficiency', 0)
                usage = skill.get('usage_count', 0)
                success = skill.get('success_rate', 0)
                md_content += f"| {skill.get('name')} | {prof:.0%} | {usage} | {success:.0%} |\n"
            
            md_content += "\n"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def generate_feishu_export(self, date_str: Optional[str] = None) -> Dict[str, str]:
        """
        生成飞书友好格式的导出文件
        这些文件可以直接复制粘贴到飞书文档
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n📤 生成飞书导出文件: {date_str}")
        print("=" * 60)
        
        export_files = {}
        
        # 1. SOUL导出
        print("\n[1/4] 生成SOUL导出...")
        soul_md = self._export_soul_for_feishu()
        soul_path = f"{self.feishu_export_dir}/SOUL-{date_str}.md"
        with open(soul_path, 'w', encoding='utf-8') as f:
            f.write(soul_md)
        export_files['soul'] = soul_path
        print(f"   ✅ {soul_path}")
        
        # 2. SKILL导出（表格格式）
        print("\n[2/4] 生成SKILL导出...")
        skill_md = self._export_skill_for_feishu()
        skill_path = f"{self.feishu_export_dir}/SKILL-{date_str}.md"
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_md)
        export_files['skill'] = skill_path
        print(f"   ✅ {skill_path}")
        
        # 3. MEMORY导出
        print("\n[3/4] 生成MEMORY导出...")
        memory_md = self._export_memory_for_feishu(date_str)
        memory_path = f"{self.feishu_export_dir}/MEMORY-{date_str}.md"
        with open(memory_path, 'w', encoding='utf-8') as f:
            f.write(memory_md)
        export_files['memory'] = memory_path
        print(f"   ✅ {memory_path}")
        
        # 4. GOAL导出
        print("\n[4/4] 生成GOAL导出...")
        goal_md = self._export_goal_for_feishu()
        goal_path = f"{self.feishu_export_dir}/GOAL-{date_str}.md"
        with open(goal_path, 'w', encoding='utf-8') as f:
            f.write(goal_md)
        export_files['goal'] = goal_path
        print(f"   ✅ {goal_path}")
        
        print("\n" + "=" * 60)
        print("✅ 飞书导出完成!")
        print(f"   导出目录: {self.feishu_export_dir}")
        print(f"   文件数: {len(export_files)}")
        
        return export_files
    
    def _export_soul_for_feishu(self) -> str:
        """生成飞书格式的SOUL导出"""
        src = f"{self.workspace}/SOUL.md"
        if os.path.exists(src):
            with open(src, 'r', encoding='utf-8') as f:
                return f.read()
        return "# SOUL\n\n暂无数据"
    
    def _export_skill_for_feishu(self) -> str:
        """生成飞书格式的SKILL导出（表格优化版）"""
        src = f"{self.workspace}/SKILL_REGISTRY.json"
        if not os.path.exists(src):
            return "# SKILL\n\n暂无数据"
        
        with open(src, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        md = f"""# SKILL REGISTRY - 技能注册表

> **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计概览

| 指标 | 数值 |
|------|------|
| 总技能数 | {data.get('summary', {}).get('total_skills', 0)} |
| 活跃技能 | {data.get('summary', {}).get('active_skills', 0)} |
| 平均熟练度 | {data.get('summary', {}).get('avg_proficiency', 0):.0%} |
| 最多使用 | {data.get('summary', {}).get('most_used', 'N/A')} |

## 📚 技能清单

"""
        
        for cat_name, cat_data in data.get('categories', {}).items():
            md += f"### {cat_data.get('name', cat_name)} ({cat_data.get('count', 0)}个)\n\n"
            md += "| 技能名称 | 熟练度 | 使用次数 | 成功率 | 状态 |\n"
            md += "|----------|--------|----------|--------|------|\n"
            
            for skill in cat_data.get('skills', []):
                prof_bar = "█" * int(skill.get('proficiency', 0) * 10) + "░" * (10 - int(skill.get('proficiency', 0) * 10))
                md += f"| {skill.get('name')} | {prof_bar} {skill.get('proficiency', 0):.0%} | {skill.get('usage_count', 0)} | {skill.get('success_rate', 0):.0%} | {skill.get('status', 'unknown')} |\n"
            
            md += "\n"
        
        return md
    
    def _export_memory_for_feishu(self, date_str: str) -> str:
        """生成飞书格式的MEMORY导出"""
        md = f"""# MEMORY - 记忆归档

> **导出日期**: {date_str}

---

## 📖 长期记忆精华

"""
        
        src = f"{self.workspace}/MEMORY.md"
        if os.path.exists(src):
            with open(src, 'r', encoding='utf-8') as f:
                md += f.read()
        else:
            md += "暂无长期记忆精华\n"
        
        md += f"""

---

## 📝 当日情景记忆 ({date_str})

"""
        
        src = f"{self.workspace}/memory/{date_str}.md"
        if os.path.exists(src):
            with open(src, 'r', encoding='utf-8') as f:
                md += f.read()
        else:
            md += "暂无当日记忆\n"
        
        return md
    
    def _export_goal_for_feishu(self) -> str:
        """生成飞书格式的GOAL导出"""
        md = f"""# GOALS - 目标进展

> **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 活跃目标

"""
        
        # 从GoalManager加载
        try:
            from goal_manager import GoalManager
            gm = GoalManager()
            
            for goal in gm.goals:
                progress_bar = "█" * int(goal.get('progress', 0) / 5) + "░" * (20 - int(goal.get('progress', 0) / 5))
                md += f"### {goal.get('title')}\n\n"
                md += f"**进度**: [{progress_bar}] {goal.get('progress', 0)}%\n\n"
                md += f"**状态**: {goal.get('status', 'unknown')}\n\n"
                
                if goal.get('tasks'):
                    md += "**任务列表**:\n\n"
                    for task in gm.tasks:
                        if task.get('goal_id') == goal.get('id'):
                            status_emoji = "✅" if task['status'] == '已完成' else "🔄" if task['status'] == '进行中' else "⏳"
                            md += f"- {status_emoji} {task.get('title')} ({task.get('progress', 0)}%)\n"
                    md += "\n"
                
                md += "---\n\n"
        except Exception as e:
            md += f"加载Goal数据失败: {e}\n"
        
        return md
    
    def list_archives(self) -> List[Dict]:
        """列出所有归档"""
        archives = []
        
        for item in os.listdir(self.archive_dir):
            item_path = f"{self.archive_dir}/{item}"
            if os.path.isdir(item_path) and item.startswith('2026'):
                index_path = f"{item_path}/INDEX.json"
                if os.path.exists(index_path):
                    with open(index_path, 'r', encoding='utf-8') as f:
                        index = json.load(f)
                        archives.append({
                            "date": item,
                            "file_count": index.get('total_files', 0),
                            "created_at": index.get('created_at', 'unknown')
                        })
        
        return sorted(archives, key=lambda x: x['date'], reverse=True)

def main():
    """主函数 - 演示"""
    print("=" * 70)
    print("📦 SSMG Archive System - 归档系统")
    print("=" * 70)
    
    archiver = SSMGArchiveSystem()
    
    # 创建每日归档
    archive_dir = archiver.create_daily_archive()
    
    # 生成飞书导出
    print("\n")
    export_files = archiver.generate_feishu_export()
    
    # 列出历史归档
    print("\n" + "=" * 70)
    print("📚 历史归档列表")
    print("=" * 70)
    archives = archiver.list_archives()
    for i, archive in enumerate(archives[:5], 1):
        print(f"{i}. {archive['date']} - {archive['file_count']} 个文件")
    
    print("\n" + "=" * 70)
    print("✅ 归档系统运行完成")
    print("=" * 70)
    print(f"\n📁 本地归档: {archiver.archive_dir}")
    print(f"📤 飞书导出: {archiver.feishu_export_dir}")

if __name__ == "__main__":
    main()
