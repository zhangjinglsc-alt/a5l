#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5: Learning System
复盘进化层 - 学习系统

功能：
1. 策略参数自动优化
2. 错误模式学习
3. 知识沉淀
4. 递归改进触发
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LearningSystem:
    """学习系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.knowledge_base_file = f"{workspace}/data/architect_5l/knowledge_base.json"
        self.improvement_log_file = f"{workspace}/data/architect_5l/improvements.json"
        
        os.makedirs(os.path.dirname(self.knowledge_base_file), exist_ok=True)
        
        # 加载知识库
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'r') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "patterns": {},
            "lessons": [],
            "improvements": []
        }
    
    def learn_from_review(self, review_data: Dict):
        """从复盘数据中学习"""
        # 1. 提取模式
        self._extract_patterns(review_data)
        
        # 2. 沉淀教训
        self._store_lessons(review_data.get("lessons", []))
        
        # 3. 触发改进
        self._trigger_improvements(review_data.get("improvements", []))
        
        # 4. 保存知识库
        self._save_knowledge_base()
    
    def _extract_patterns(self, review_data: Dict):
        """提取交易模式"""
        date = review_data.get("date", "")
        
        # 胜率模式
        win_rate = review_data.get("win_rate", 0)
        if win_rate < 0.4:
            pattern_key = f"low_win_rate_{date}"
            self.knowledge_base["patterns"][pattern_key] = {
                "type": "low_win_rate",
                "date": date,
                "value": win_rate,
                "threshold": 0.4,
                "action": "检查策略有效性，考虑市场环境变化"
            }
        
        # 连续亏损模式
        if review_data.get("losing_trades", 0) >= 3:
            pattern_key = f"consecutive_losses_{date}"
            self.knowledge_base["patterns"][pattern_key] = {
                "type": "consecutive_losses",
                "date": date,
                "count": review_data.get("losing_trades", 0),
                "action": "触发风控暂停机制"
            }
    
    def _store_lessons(self, lessons: List[str]):
        """存储教训"""
        for lesson in lessons:
            lesson_entry = {
                "content": lesson,
                "learned_at": datetime.now().isoformat(),
                "applied": False
            }
            self.knowledge_base["lessons"].append(lesson_entry)
    
    def _trigger_improvements(self, improvements: List[str]):
        """触发改进"""
        for improvement in improvements:
            improvement_entry = {
                "description": improvement,
                "proposed_at": datetime.now().isoformat(),
                "status": "pending",
                "implemented_at": None
            }
            self.knowledge_base["improvements"].append(improvement_entry)
            
            # 记录到改进日志
            self._log_improvement(improvement_entry)
    
    def _log_improvement(self, improvement: Dict):
        """记录改进"""
        improvements = []
        if os.path.exists(self.improvement_log_file):
            with open(self.improvement_log_file, 'r') as f:
                improvements = json.load(f)
        
        improvements.append(improvement)
        
        with open(self.improvement_log_file, 'w') as f:
            json.dump(improvements, f, indent=2, ensure_ascii=False)
    
    def _save_knowledge_base(self):
        """保存知识库"""
        self.knowledge_base["updated_at"] = datetime.now().isoformat()
        
        with open(self.knowledge_base_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        return {
            "total_patterns": len(self.knowledge_base.get("patterns", {})),
            "total_lessons": len(self.knowledge_base.get("lessons", [])),
            "total_improvements": len(self.knowledge_base.get("improvements", [])),
            "pending_improvements": len([i for i in self.knowledge_base.get("improvements", []) if i.get("status") == "pending"]),
            "version": self.knowledge_base.get("version", "1.0")
        }
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        stats = self.get_learning_stats()
        
        report = f"""# 🧠 学习系统报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**知识库版本**: {stats['version']}

---

## 📊 学习统计

| 指标 | 数值 |
|------|------|
| 识别模式数 | {stats['total_patterns']} |
| 沉淀教训数 | {stats['total_lessons']} |
| 改进建议数 | {stats['total_improvements']} |
| 待实施改进 | {stats['pending_improvements']} |

---

## 🔍 已识别模式

"""
        
        for pattern_id, pattern in list(self.knowledge_base.get("patterns", {}).items())[-10:]:
            report += f"- **{pattern['type']}** ({pattern['date']}): {pattern.get('action', 'N/A')}\n"
        
        report += """
---

## 📝 最近教训

"""
        
        for lesson in self.knowledge_base.get("lessons", [])[-5:]:
            status = "✅ 已应用" if lesson.get("applied") else "⏳ 待应用"
            report += f"- {lesson['content'][:80]}... [{status}]\n"
        
        report += """
---

## 🚀 待实施改进

"""
        
        for imp in self.knowledge_base.get("improvements", []):
            if imp.get("status") == "pending":
                report += f"- ⏳ {imp['description'][:80]}...\n"
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🧠 学习系统 (Layer 5)")
    print("=" * 70)
    
    learning = LearningSystem()
    
    # 模拟学习
    print("\n📚 从复盘数据学习...")
    review_data = {
        "date": "2026-05-01",
        "total_trades": 5,
        "winning_trades": 2,
        "losing_trades": 3,
        "win_rate": 0.4,
        "total_pnl": -2500,
        "lessons": [
            "盈亏比 1.5:1 偏低，建议优化止损策略",
            "连续亏损警示: 当日发生 3 笔亏损交易"
        ],
        "improvements": [
            "风控增强: 建议添加连续亏损3次后自动暂停机制",
            "止损优化: 检查止损单是否有效执行"
        ]
    }
    
    learning.learn_from_review(review_data)
    
    print("✅ 学习完成！")
    
    # 显示统计
    stats = learning.get_learning_stats()
    print(f"\n📊 知识库统计:")
    print(f"  识别模式: {stats['total_patterns']} 个")
    print(f"  沉淀教训: {stats['total_lessons']} 条")
    print(f"  改进建议: {stats['total_improvements']} 条")
    print(f"  待实施: {stats['pending_improvements']} 条")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 学习报告:")
    report = learning.generate_learning_report()
    print(report[:800] + "...")

if __name__ == "__main__":
    main()
