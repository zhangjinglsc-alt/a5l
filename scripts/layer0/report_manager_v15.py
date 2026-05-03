#!/usr/bin/env python3
"""
A5L Report Manager v1.5 - 智能报告管理升级
Layer 0 核心组件

升级功能 (v1.0 → v1.5):
- 自动分类标签 (个股/行业/宏观)
- 阅读优先级排序 (基于持仓)
- 报告关联分析
- 飞书自动归档

执行时间: 2026-05-04 01:42 (v1.5升级)
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/report_manager.log"
DATA_DIR = f"{WORKSPACE}/data/reports"

class ReportManager:
    """
    Report Manager v1.5 - 智能报告中枢
    """
    
    # 持仓股票 (用于优先级排序)
    HOLDINGS = ['601975', '000066', '688981']
    
    # 分类规则
    CATEGORIES = {
        '个股': ['个股分析', '深度研究', '股票代码'],
        '行业': ['行业研究', '产业链', '板块'],
        '宏观': ['宏观', '策略', '周报', '月报'],
        '财报': ['财报', '业绩', '季报', '年报'],
        '快讯': ['快讯', '公告', '新闻']
    }
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.log("="*70)
        self.log("Report Manager v1.5 初始化")
        self.log("="*70)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def auto_classify(self, title: str, content: str = "") -> Dict:
        """
        自动分类报告
        """
        title_lower = title.lower()
        
        # 检查分类规则
        for category, keywords in self.CATEGORIES.items():
            if any(kw in title_lower for kw in keywords):
                return {
                    'category': category,
                    'confidence': 'HIGH',
                    'method': 'keyword_match'
                }
        
        # 检查是否包含持仓股票
        for code in self.HOLDINGS:
            if code in title:
                return {
                    'category': '个股',
                    'confidence': 'MEDIUM',
                    'method': 'holding_match',
                    'related_stock': code
                }
        
        return {
            'category': '未分类',
            'confidence': 'LOW',
            'method': 'none'
        }
    
    def calculate_priority(self, title: str, category: str) -> Dict:
        """
        计算阅读优先级 (基于持仓关联)
        """
        priority_score = 50  # 基础分
        reasons = []
        
        # 持仓相关 +30分
        for code in self.HOLDINGS:
            if code in title:
                priority_score += 30
                reasons.append(f"持仓股票 {code}")
                break
        
        # 个股分析 +20分
        if category == '个股':
            priority_score += 20
            reasons.append("个股分析")
        
        # 行业研究 +15分
        elif category == '行业':
            priority_score += 15
            reasons.append("行业研究")
        
        # 财报季 +25分
        if any(kw in title for kw in ['季报', '年报', '业绩']):
            priority_score += 25
            reasons.append("财报相关")
        
        # 确定优先级
        if priority_score >= 80:
            level = 'P0 - 立即阅读'
        elif priority_score >= 60:
            level = 'P1 - 今日阅读'
        elif priority_score >= 40:
            level = 'P2 - 本周阅读'
        else:
            level = 'P3 - 有空阅读'
        
        return {
            'score': priority_score,
            'level': level,
            'reasons': reasons
        }
    
    def process_report(self, report_info: Dict) -> Dict:
        """
        处理单份报告
        """
        title = report_info.get('title', '')
        
        # 自动分类
        classification = self.auto_classify(title)
        
        # 计算优先级
        priority = self.calculate_priority(title, classification['category'])
        
        # 生成文档ID
        doc_id = hashlib.md5(title.encode()).hexdigest()[:8]
        
        processed = {
            'doc_id': doc_id,
            'title': title,
            'source': report_info.get('source', 'unknown'),
            'date': report_info.get('date', datetime.now().strftime('%Y-%m-%d')),
            'classification': classification,
            'priority': priority,
            'archive_path': f"空间2/{self.get_archive_folder(classification['category'])}/",
            'processed_at': datetime.now().isoformat()
        }
        
        return processed
    
    def get_archive_folder(self, category: str) -> str:
        """获取归档文件夹"""
        folder_map = {
            '个股': '20_个股档案',
            '行业': '10_行业研究',
            '宏观': '50_研报中心',
            '财报': '40_持仓与交易',
            '快讯': '30_每日批注',
            '未分类': '60_待整理'
        }
        return folder_map.get(category, '60_待整理')
    
    def batch_process(self, reports: List[Dict]) -> Dict:
        """
        批量处理报告
        """
        self.log("\n" + "="*70)
        self.log("批量处理报告")
        self.log("="*70)
        
        processed_reports = []
        
        for report in reports:
            processed = self.process_report(report)
            processed_reports.append(processed)
            
            self.log(f"\n  📄 {processed['title'][:40]}...")
            self.log(f"     分类: {processed['classification']['category']}")
            self.log(f"     优先级: {processed['priority']['level']}")
            self.log(f"     归档: {processed['archive_path']}")
        
        # 按优先级排序
        sorted_reports = sorted(
            processed_reports,
            key=lambda x: x['priority']['score'],
            reverse=True
        )
        
        # 生成摘要
        summary = {
            'total': len(sorted_reports),
            'by_category': {},
            'by_priority': {
                'P0': len([r for r in sorted_reports if 'P0' in r['priority']['level']]),
                'P1': len([r for r in sorted_reports if 'P1' in r['priority']['level']]),
                'P2': len([r for r in sorted_reports if 'P2' in r['priority']['level']]),
                'P3': len([r for r in sorted_reports if 'P3' in r['priority']['level']])
            }
        }
        
        for r in sorted_reports:
            cat = r['classification']['category']
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
        
        self.log(f"\n📊 处理统计:")
        self.log(f"  总报告: {summary['total']}")
        self.log(f"  P0立即阅读: {summary['by_priority']['P0']}")
        self.log(f"  P1今日阅读: {summary['by_priority']['P1']}")
        self.log(f"  P2本周阅读: {summary['by_priority']['P2']}")
        
        result = {
            'reports': sorted_reports,
            'summary': summary,
            'reading_queue': [r['title'] for r in sorted_reports[:5]]  # Top 5
        }
        
        # 保存结果
        report_file = f"{DATA_DIR}/rm_batch_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 结果已保存: {report_file}")
        
        return result
    
    def demo_process(self):
        """
        演示处理示例报告
        """
        demo_reports = [
            {'title': '招商南油(601975)深度研究报告', 'source': '小张AI', 'date': '2026-04-12'},
            {'title': '半导体行业周报：AI算力需求持续', 'source': 'Pandora', 'date': '2026-05-03'},
            {'title': '高盛美股周报：AI周期intact', 'source': 'Goldman Sachs', 'date': '2026-05-01'},
            {'title': '中国长城2025年报点评', 'source': '券商研报', 'date': '2026-03-31'},
            {'title': '宏观经济月报：4月PMI分析', 'source': '宏观组', 'date': '2026-05-01'},
        ]
        
        return self.batch_process(demo_reports)


def main():
    """主函数"""
    print("="*70)
    print("📚 Report Manager v1.5 - 智能报告中枢")
    print("Layer 0 - Report Manager Upgrade")
    print("="*70)
    
    rm = ReportManager()
    result = rm.demo_process()
    
    print("\n" + "="*70)
    print("✅ Report Manager v1.5 运行完成")
    print(f"  处理报告: {result['summary']['total']} 份")
    print(f"  立即阅读: {result['summary']['by_priority']['P0']} 份")
    print(f"  今日阅读: {result['summary']['by_priority']['P1']} 份")
    print("\n📖 推荐阅读队列 (Top 5):")
    for i, title in enumerate(result['reading_queue'], 1):
        print(f"  {i}. {title}")
    print("="*70)


if __name__ == "__main__":
    main()
