"""
REPORT-MANAGER SKILL Package
研报管理SKILL包

提供专业的投研文档管理功能:
- 研报自动分类归档
- 全文检索
- 标签管理
- 飞书云文档同步
- 统计分析

Author: A5L
Version: 1.0.0
Date: 2026-05-02
"""

__version__ = "1.0.0"
__author__ = "A5L"

from .SKILL import (
    ResearchReportManager,
    ResearchReport,
    ReportCategory,
    ReportFolder
)

__all__ = [
    'ResearchReportManager',
    'ResearchReport',
    'ReportCategory',
    'ReportFolder'
]
