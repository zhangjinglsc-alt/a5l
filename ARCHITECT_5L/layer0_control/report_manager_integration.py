#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Manager Integration for A5L
研报管理器A5L集成插件

功能:
1. 分析结果自动归档
2. 研报自动上传飞书
3. 与SKILL系统深度集成
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# 添加SKILL路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.REPORT_MANAGER.SKILL import ResearchReportManager, ResearchReport


class ReportManagerPlugin:
    """
    A5L研报管理插件
    
    使用示例:
        plugin = ReportManagerPlugin()
        
        # 分析完成后自动归档
        analysis_result = analyze_stock("300750.SZ")
        plugin.auto_archive(analysis_result)
        
        # 搜索历史研报
        reports = plugin.search_reports(stock_code="300750.SZ")
    """
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = "/workspace/projects/workspace/output/reports"
        
        self.manager = ResearchReportManager(base_path=base_path)
        self.feishu_sync = None  # 延迟初始化
        
        print(f"📁 Report Manager Plugin initialized")
    
    def auto_archive(self, 
                     analysis_result: Dict,
                     file_path: Optional[str] = None,
                     auto_upload_feishu: bool = True) -> ResearchReport:
        """
        自动归档分析结果
        
        Args:
            analysis_result: 分析结果字典
            file_path: 报告文件路径
            auto_upload_feishu: 是否自动上传飞书
            
        Returns:
            ResearchReport: 研报对象
        """
        # 从分析结果提取信息
        stock_code = analysis_result.get('stock_code', 'UNKNOWN')
        stock_name = analysis_result.get('stock_name', stock_code)
        
        # 构建标题
        title = f"{stock_name} ({stock_code}) 深度分析报告"
        
        # 提取评级
        rating = self._extract_rating(analysis_result)
        
        # 提取行业
        industry = analysis_result.get('industry', '其他')
        
        # 提取标签
        tags = self._extract_tags(analysis_result)
        
        # 添加研报
        report = self.manager.add_report(
            file_path=file_path or analysis_result.get('report_path', ''),
            title=title,
            stock_code=stock_code,
            stock_name=stock_name,
            source="A5L智能分析",
            report_date=datetime.now().strftime("%Y-%m-%d"),
            rating=rating,
            industry=industry,
            tags=tags,
            auto_organize=True
        )
        
        # 自动上传飞书
        if auto_upload_feishu:
            self._upload_to_feishu(report)
        
        return report
    
    def _extract_rating(self, analysis_result: Dict) -> Optional[str]:
        """从分析结果提取评级"""
        recommendation = analysis_result.get('recommendation', {})
        final_rec = recommendation.get('final', '')
        
        # 映射到标准评级
        rating_map = {
            '买入': '买入',
            '增持': '增持',
            '中性': '中性',
            '观望': '中性',
            '减持': '减持',
            '卖出': '卖出',
            '回避': '减持'
        }
        
        for key, value in rating_map.items():
            if key in final_rec:
                return value
        
        # 根据评分判断
        score = analysis_result.get('overall_score', 0)
        if score >= 80:
            return '买入'
        elif score >= 60:
            return '增持'
        elif score >= 40:
            return '中性'
        else:
            return '减持'
    
    def _extract_tags(self, analysis_result: Dict) -> List[str]:
        """从分析结果提取标签"""
        tags = []
        
        # 分析方法标签
        if 'uzi_score' in analysis_result:
            tags.append('UZI分析')
        if 'value_cell' in analysis_result:
            tags.append('VALUE-CELL')
        if 'risk_score' in analysis_result:
            tags.append('风险审查')
        
        # 评级标签
        rating = self._extract_rating(analysis_result)
        if rating:
            tags.append(rating)
        
        # 行业标签
        industry = analysis_result.get('industry')
        if industry:
            tags.append(industry)
        
        return tags
    
    def _upload_to_feishu(self, report: ResearchReport):
        """上传研报到飞书"""
        try:
            from skills.REPORT_MANAGER.feishu_sync import FeishuSync
            
            if self.feishu_sync is None:
                self.feishu_sync = FeishuSync()
            
            self.feishu_sync.upload_report(report)
            print(f"☁️ Uploaded to Feishu: {report.title}")
            
        except Exception as e:
            print(f"⚠️ Failed to upload to Feishu: {e}")
    
    def search_reports(self, **kwargs) -> List[ResearchReport]:
        """搜索研报"""
        return self.manager.search_reports(**kwargs)
    
    def get_latest_reports(self, limit: int = 10) -> List[ResearchReport]:
        """获取最新研报"""
        return self.manager.get_latest_reports(limit=limit)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.manager.get_statistics()
    
    def get_reports_by_stock(self, stock_code: str) -> List[ResearchReport]:
        """获取某只股票的研报"""
        return self.manager.get_reports_by_stock(stock_code)
    
    def export_catalog(self, output_path: str):
        """导出研报目录"""
        self.manager.export_catalog(output_path)


# 便捷函数
def archive_analysis_result(analysis_result: Dict, 
                           file_path: Optional[str] = None) -> ResearchReport:
    """
    便捷函数：归档分析结果
    
    使用示例:
        result = analyze_stock("300750.SZ")
        report = archive_analysis_result(result)
    """
    plugin = ReportManagerPlugin()
    return plugin.auto_archive(analysis_result, file_path)


def search_reports(**kwargs) -> List[ResearchReport]:
    """
    便捷函数：搜索研报
    
    使用示例:
        reports = search_reports(stock_code="300750.SZ", rating="买入")
    """
    plugin = ReportManagerPlugin()
    return plugin.search_reports(**kwargs)


if __name__ == "__main__":
    print("=" * 80)
    print("📁 Report Manager Plugin for A5L - Test")
    print("=" * 80)
    
    # 测试插件
    plugin = ReportManagerPlugin()
    
    # 模拟分析结果
    test_result = {
        "stock_code": "300750.SZ",
        "stock_name": "宁德时代",
        "overall_score": 85.5,
        "recommendation": {
            "final": "买入"
        },
        "industry": "新能源",
        "uzi_score": 82.0,
        "value_cell": 78.5,
        "risk_score": 85.0
    }
    
    # 测试归档
    print("\n[1/3] Testing auto archive...")
    try:
        report = plugin.auto_archive(test_result, auto_upload_feishu=False)
        print(f"✅ Archived: {report.title}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 测试搜索
    print("\n[2/3] Testing search...")
    results = plugin.search_reports(stock_code="300750.SZ")
    print(f"✅ Found {len(results)} reports")
    
    # 测试统计
    print("\n[3/3] Testing statistics...")
    stats = plugin.get_statistics()
    print(f"✅ Total reports: {stats['total_reports']}")
    
    print("\n" + "=" * 80)
    print("✅ Report Manager Plugin test completed!")
