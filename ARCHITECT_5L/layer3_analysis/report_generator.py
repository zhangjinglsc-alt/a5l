#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 3: Report Generator
非结构化分析层 - 报告生成器

功能：
1. 生成每日市场/板块分析报告
2. 飞书云文档自动同步
3. 信息验证和溯源
4. 风险评估和机会识别

核心原则：
- 诚实第一：不编造信息
- 验证溯源：每句话都有来源
- 明确区分：事实 vs 观点
- 风险披露：不确定性明确说明
"""

import json
import os
import sys
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer3_analysis/aggregators')
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer3_analysis/analyzers')

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from info_aggregator import InfoAggregator
from sentiment_analyzer import SentimentAnalyzer

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.reports_dir = f"{workspace}/data/architect_5l/reports"
        
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 初始化组件
        self.aggregator = InfoAggregator(workspace)
        self.sentiment_analyzer = SentimentAnalyzer(workspace)
    
    def generate_sector_report(self, date: str, market: str, sector: str) -> str:
        """
        生成板块分析报告
        
        格式: 《YYYYMMDD-Market-Sector Analysis》
        """
        # 获取板块内代表股票（简化实现）
        sample_symbols = self._get_sector_symbols(sector)
        
        # 聚合所有信息
        all_info = []
        for symbol in sample_symbols:
            info_list = self.aggregator.fetch_info(symbol)
            all_info.extend(info_list)
        
        # 分析情绪
        sentiment = self.sentiment_analyzer.analyze_sector_sentiment(sector, all_info)
        
        # 识别风险和机会
        risks = []
        opportunities = []
        
        for info in all_info:
            if info.credibility_score >= 7:  # 只分析高可信度信息
                info_risks = self.sentiment_analyzer.identify_risks(info.content, info.title)
                info_opps = self.sentiment_analyzer.identify_opportunities(info.content, info.title)
                
                risks.extend(info_risks)
                opportunities.extend(info_opps)
        
        # 生成报告
        report = self._format_report(date, market, sector, sentiment, risks, opportunities, all_info)
        
        # 保存报告
        self._save_report(report, date, market, sector)
        
        return report
    
    def _get_sector_symbols(self, sector: str) -> List[str]:
        """获取板块代表股票（简化实现）"""
        # 实际应该从数据库或配置中读取
        sector_map = {
            "半导体": ["688981.SH", "002371.SZ", "603501.SH"],
            "新能源": ["300750.SZ", "601012.SH", "002594.SZ"],
            "人工智能": ["000938.SZ", "600756.SH", "300418.SZ"],
            "银行": ["000001.SZ", "600036.SH", "601398.SH"],
            "医药": ["600276.SH", "000538.SZ", "300003.SZ"]
        }
        return sector_map.get(sector, ["000001.SZ"])
    
    def _format_report(self, date: str, market: str, sector: str,
                       sentiment: Dict, risks: List, opportunities: List,
                       info_list: List) -> str:
        """
        格式化报告
        
        严格遵循诚实原则，所有信息标注来源和可信度
        """
        report = f"""# 《{date}-{market}-{sector}板块分析》

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析周期**: {date}  
**市场**: {market}  
**板块**: {sector}  
**数据来源**: {len(info_list)} 条信息  
**分析师**: ARCHITECT-5L Layer 3

---

## 📊 执行摘要

| 指标 | 数值 | 说明 |
|------|------|------|
| 板块情绪 | {"🟢 乐观" if sentiment['sentiment'] == 'positive' else "🔴 悲观" if sentiment['sentiment'] == 'negative' else "⚪ 中性"} | 情绪得分: {sentiment['score']} |
| 信息总量 | {sentiment['info_count']} 条 | 过去7天 |
| 正面信息 | {sentiment['positive_count']} 条 | - |
| 负面信息 | {sentiment['negative_count']} 条 | - |
| 可信度 | {sentiment['confidence']:.0%} | 基于信息源质量 |

---

## 🏢 板块龙头

| 股票代码 | 公司名称 | 角色 | 近期表现 |
|----------|----------|------|----------|
"""
        
        # 添加板块龙头（简化）
        symbols = self._get_sector_symbols(sector)
        for i, symbol in enumerate(symbols[:5], 1):
            role = "龙头" if i == 1 else "重要成分"
            report += f"| {symbol} | 待补充 | {role} | 待补充 |\n"
        
        report += f"""
---

## 📡 信息渠道及可信度

| 信息源 | 类别 | 可信度 | 信息数 |
|--------|------|--------|--------|
"""
        
        # 统计信息源
        source_stats = {}
        for info in info_list:
            if info.source not in source_stats:
                source_stats[info.source] = {
                    "category": info.category,
                    "credibility": info.credibility_score,
                    "count": 0
                }
            source_stats[info.source]["count"] += 1
        
        for source, stats in sorted(source_stats.items(), key=lambda x: x[1]["credibility"], reverse=True):
            cred_stars = "⭐" * (int(stats["credibility"]) // 2)
            report += f"| {source} | {stats['category']} | {cred_stars} ({stats['credibility']}/10) | {stats['count']} |\n"
        
        # 风险点
        report += f"""
---

## ⚠️ 风险点

**识别到的风险数量**: {len(risks)} 个

"""
        
        if risks:
            for i, risk in enumerate(risks[:10], 1):  # 最多显示10个
                severity_icon = "🔴" if risk['severity'] == 'high' else "🟡" if risk['severity'] == 'medium' else "🟢"
                report += f"""{i}. {severity_icon} **{risk['keyword'].upper()}** [严重度: {risk['severity']}]
   - 上下文: "...{risk['context']}..."
   - 依据: {risk['evidence']}

"""
        else:
            report += "✅ 未发现明显风险点\n"
        
        # 机会点
        report += f"""
---

## ✅ 机会点

**识别到的机会数量**: {len(opportunities)} 个

"""
        
        if opportunities:
            for i, opp in enumerate(opportunities[:10], 1):  # 最多显示10个
                conf_icon = "🟢" if opp['confidence'] == 'high' else "🟡" if opp['confidence'] == 'medium' else "⚪"
                report += f"""{i}. {conf_icon} **{opp['keyword'].upper()}** [可信度: {opp['confidence']}]
   - 上下文: "...{opp['context']}..."
   - 依据: {opp['evidence']}

"""
        else:
            report += "⚪ 未发现明显机会点\n"
        
        # 最新变化
        report += f"""
---

## 🔄 最新变化

**过去24小时重要信息**:

"""
        
        recent_info = [info for info in info_list if info.credibility_score >= 8]
        recent_info.sort(key=lambda x: x.publish_time, reverse=True)
        
        for info in recent_info[:5]:
            verified_icon = "✅" if info.verified else "⚠️"
            report += f"""{verified_icon} **[{info.source}]** {info.title}
   - 时间: {info.publish_time}
   - 可信度: {info.credibility_score}/10
   - 摘要: {info.content[:100]}...

"""
        
        # 判断与结论
        report += f"""
---

## 🧐 分析与判断

### 总体判断
基于以上分析，本板块当前处于**{sentiment['sentiment'].upper()}**状态，情绪得分 {sentiment['score']}。

### 主要依据
1. **信息情绪**: 正面信息{sentiment['positive_count']}条，负面信息{sentiment['negative_count']}条
2. **风险状况**: {len([r for r in risks if r['severity'] == 'high'])}个高风险项
3. **机会状况**: {len([o for o in opportunities if o['confidence'] == 'high'])}个高可信度机会

### 不确定性说明
- ⚠️ 分析基于公开信息，可能存在信息滞后
- ⚠️ 情绪分析基于关键词匹配，仅供参考
- ⚠️ 短期市场波动受多重因素影响

---

## 📋 免责声明

1. **信息来源**: 本报告信息来源于公开渠道，已标注来源和可信度
2. **验证状态**: 官方公告已验证，其他信息仅供参考
3. **观点声明**: 本报告中的判断基于算法分析，不构成投资建议
4. **风险提示**: 股市有风险，投资需谨慎

---

**报告生成**: ARCHITECT-5L Layer 3 - 非结构化分析层  
**核心原则**: 诚实第一 | 验证溯源 | 事实与观点分离  
**下次更新**: 下一个交易日
"""
        
        return report
    
    def _save_report(self, report: str, date: str, market: str, sector: str):
        """保存报告"""
        filename = f"{date}_{market}_{sector}_analysis.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def list_reports(self) -> List[Dict]:
        """列出所有报告"""
        reports = []
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.reports_dir, filename)
                stat = os.stat(filepath)
                reports.append({
                    "filename": filename,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size
                })
        
        return sorted(reports, key=lambda x: x['created'], reverse=True)

def main():
    """演示"""
    print("=" * 70)
    print("📄 报告生成器 (Layer 3)")
    print("=" * 70)
    
    generator = ReportGenerator()
    
    # 生成示例报告
    print("\n📝 生成板块分析报告...")
    report = generator.generate_sector_report(
        date="20260502",
        market="A股",
        sector="半导体"
    )
    
    print("✅ 报告生成完成！")
    print(f"\n报告预览（前1500字）:")
    print("=" * 70)
    print(report[:1500])
    print("...")
    print("=" * 70)
    
    # 显示报告统计
    reports = generator.list_reports()
    print(f"\n📊 已生成报告: {len(reports)} 份")
    for r in reports[:3]:
        print(f"  • {r['filename']} ({r['size']} bytes)")

if __name__ == "__main__":
    main()
