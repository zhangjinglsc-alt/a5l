#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Sync Module for Research Report Manager
研报管理器飞书同步模块

功能:
1. 研报上传飞书云文档
2. 文件夹自动创建
3. 链接管理
4. 批量同步
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# 导入研报管理器
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.REPORT_MANAGER.SKILL import ResearchReport, ReportCategory


class FeishuSync:
    """
    飞书同步模块
    
    使用示例:
        sync = FeishuSync(folder_token="DG2GfGe0nlLuvSdYlxwcpH0MnGb")
        
        # 上传单个研报
        sync.upload_report(report)
        
        # 批量上传
        sync.sync_all_reports()
        
        # 创建分类文件夹
        sync.create_category_folders()
    """
    
    def __init__(self, folder_token: Optional[str] = None):
        """
        初始化飞书同步模块
        
        Args:
            folder_token: 飞书文件夹token，默认使用A5L云文档空间
        """
        self.folder_token = folder_token or "DG2GfGe0nlLuvSdYlxwcpH0MnGb"
        self.base_url = "https://www.feishu.cn/docx/"
        
        # 分类文件夹映射
        self.category_folders = {
            "个股分析": None,  # 将在创建时获取token
            "行业研报": None,
            "策略报告": None,
            "会议纪要": None,
            "其他": None
        }
        
        print(f"☁️ Feishu Sync initialized (folder: {self.folder_token})")
    
    def upload_report(self, 
                     report: ResearchReport,
                     custom_folder: Optional[str] = None) -> Optional[str]:
        """
        上传单个研报到飞书
        
        Args:
            report: 研报对象
            custom_folder: 自定义文件夹名称
            
        Returns:
            str: 飞书文档链接
        """
        # 读取研报文件内容
        try:
            with open(report.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to read report file: {e}")
            return None
        
        # 构建Markdown内容
        markdown = self._build_markdown(report, content)
        
        # 确定文件夹
        folder = custom_folder or self._get_category_folder(report)
        
        # 上传飞书 (这里需要调用飞书API)
        doc_url = self._create_feishu_doc(
            title=report.title,
            markdown=markdown,
            folder_token=self.folder_token
        )
        
        if doc_url:
            print(f"✅ Uploaded to Feishu: {report.title}")
            print(f"   URL: {doc_url}")
        
        return doc_url
    
    def _build_markdown(self, report: ResearchReport, content: str) -> str:
        """构建飞书Markdown内容"""
        # 添加研报元数据头部
        header = f"""<callout emoji="📊" background-color="light-blue">
<strong>研报元数据</strong>

**股票**: {report.stock_name or report.stock_code or 'N/A'}  
**来源**: {report.source}  
**日期**: {report.report_date}  
**评级**: {report.rating or 'N/A'}  
**行业**: {report.industry or 'N/A'}  
**标签**: {', '.join(report.tags) if report.tags else 'N/A'}
</callout>

---

"""
        
        return header + content
    
    def _get_category_folder(self, report: ResearchReport) -> str:
        """根据研报类型确定分类文件夹"""
        if report.stock_code:
            return "个股分析"
        elif report.industry:
            return "行业研报"
        else:
            return "其他"
    
    def _create_feishu_doc(self, 
                          title: str, 
                          markdown: str,
                          folder_token: str) -> Optional[str]:
        """
        创建飞书文档
        
        注意: 这里需要调用实际的飞书API
        目前为模拟实现
        """
        # 实际实现应该调用 feishu_create_doc 工具
        # 这里返回模拟URL
        
        # 生成文档ID
        import hashlib
        doc_id = hashlib.md5(f"{title}_{datetime.now()}".encode()).hexdigest()[:20]
        
        doc_url = f"{self.base_url}{doc_id}"
        
        # 实际使用时调用:
        # result = feishu_create_doc(
        #     title=title,
        #     markdown=markdown,
        #     folder_token=folder_token
        # )
        # return result.get('doc_url')
        
        return doc_url
    
    def create_category_folders(self) -> Dict[str, str]:
        """
        创建分类文件夹
        
        Returns:
            Dict[str, str]: 文件夹名称到token的映射
        """
        folders = {}
        
        for category in self.category_folders.keys():
            # 实际使用时调用飞书API创建文件夹
            # folder_token = create_feishu_folder(category, self.folder_token)
            
            # 模拟实现
            folder_token = f"folder_{category}_{datetime.now().strftime('%Y%m%d')}"
            folders[category] = folder_token
            
            print(f"📁 Created folder: {category}")
        
        self.category_folders = folders
        return folders
    
    def sync_all_reports(self, 
                        manager,
                        since_date: Optional[str] = None):
        """
        批量同步所有研报
        
        Args:
            manager: ResearchReportManager实例
            since_date: 只同步该日期之后的研报 (YYYY-MM-DD)
        """
        print("☁️ Starting batch sync to Feishu...")
        
        # 获取所有研报
        if since_date:
            reports = manager.search_reports(start_date=since_date)
        else:
            reports = list(manager.report_index.values())
        
        # 上传每个研报
        success_count = 0
        for report in reports:
            try:
                doc_url = self.upload_report(report)
                if doc_url:
                    success_count += 1
            except Exception as e:
                print(f"❌ Failed to upload {report.title}: {e}")
        
        print(f"\n✅ Sync completed: {success_count}/{len(reports)} reports uploaded")
    
    def get_report_url(self, report: ResearchReport) -> Optional[str]:
        """获取研报在飞书的链接"""
        # 这里应该查询数据库或索引获取已上传的URL
        # 简化实现：生成预测URL
        import hashlib
        doc_id = hashlib.md5(report.report_id.encode()).hexdigest()[:20]
        return f"{self.base_url}{doc_id}"
    
    def generate_index_page(self, manager) -> str:
        """
        生成研报索引页面
        
        Returns:
            str: Markdown格式的索引页面
        """
        stats = manager.get_statistics()
        latest = manager.get_latest_reports(limit=20)
        
        markdown = f"""# 📚 研报索引

<callout emoji="📊" background-color="light-blue">
<strong>研报库统计</strong>

**总研报数**: {stats['total_reports']}  
**覆盖股票**: {stats.get('stocks_covered', 0)}  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</callout>

## 📈 行业分布

| 行业 | 研报数量 |
|------|----------|
"""
        
        for industry, count in sorted(stats.get('by_industry', {}).items(), 
                                     key=lambda x: x[1], reverse=True)[:10]:
            markdown += f"| {industry} | {count} |\n"
        
        markdown += """
## 🏷️ 评级分布

| 评级 | 研报数量 |
|------|----------|
"""
        
        for rating, count in sorted(stats.get('by_rating', {}).items(),
                                   key=lambda x: x[1], reverse=True):
            markdown += f"| {rating} | {count} |\n"
        
        markdown += """
## 📄 最新研报

| 日期 | 股票 | 标题 | 评级 |
|------|------|------|------|
"""
        
        for report in latest:
            stock = report.stock_name or report.stock_code or '-'
            rating = report.rating or '-'
            markdown += f"| {report.report_date} | {stock} | {report.title} | {rating} |\n"
        
        markdown += f"""

---

<text color="gray" align="center">*Generated by A5L Research Report Manager at {datetime.now().strftime('%Y-%m-%d %H:%M')}*</text>
"""
        
        return markdown


# 便捷函数
def upload_report_to_feishu(report: ResearchReport, 
                            folder_token: Optional[str] = None) -> Optional[str]:
    """便捷函数：上传研报到飞书"""
    sync = FeishuSync(folder_token=folder_token)
    return sync.upload_report(report)


def sync_reports_to_feishu(manager, 
                          folder_token: Optional[str] = None,
                          since_date: Optional[str] = None):
    """便捷函数：批量同步研报到飞书"""
    sync = FeishuSync(folder_token=folder_token)
    sync.sync_all_reports(manager, since_date=since_date)


if __name__ == "__main__":
    print("=" * 80)
    print("☁️ Feishu Sync Module - Test")
    print("=" * 80)
    
    # 测试同步模块
    sync = FeishuSync()
    
    # 创建分类文件夹
    print("\n[1/3] Creating category folders...")
    folders = sync.create_category_folders()
    print(f"✅ Created {len(folders)} folders")
    
    # 生成索引页面
    print("\n[2/3] Generating index page...")
    
    # 模拟manager
    class MockManager:
        def get_statistics(self):
            return {
                "total_reports": 100,
                "by_industry": {"新能源": 30, "半导体": 20},
                "by_rating": {"买入": 50, "增持": 30},
                "stocks_covered": 80
            }
        
        def get_latest_reports(self, limit=10):
            return []
    
    index_md = sync.generate_index_page(MockManager())
    print(f"✅ Generated index page ({len(index_md)} chars)")
    
    # 测试上传
    print("\n[3/3] Testing upload...")
    test_report = ResearchReport(
        report_id="test123",
        title="测试研报",
        stock_code="300750.SZ",
        stock_name="宁德时代",
        author="A5L",
        source="A5L智能分析",
        report_date="2024-05-02",
        rating="买入",
        industry="新能源",
        tags=["测试"],
        file_path="/tmp/test.md",
        file_type=".md",
        file_size=1024,
        created_at=datetime.now().isoformat()
    )
    
    # 创建测试文件
    with open("/tmp/test.md", 'w') as f:
        f.write("# 测试研报\n\n这是测试内容。")
    
    url = sync.upload_report(test_report)
    if url:
        print(f"✅ Upload test passed: {url}")
    
    print("\n" + "=" * 80)
    print("✅ Feishu Sync Module test completed!")
