#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL基类 v1.0
所有SKILL都应该继承这个基类
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from abc import ABC, abstractmethod

class SkillBase(ABC):
    """SKILL基类"""
    
    # SKILL元数据（子类必须重写）
    METADATA = {
        "id": "skill_base",
        "name": "SKILL基类",
        "version": "1.0.0",
        "category": "base",
        "description": "所有SKILL的基类",
        "author": "Evolution Daemon",
        "created_at": "2026-05-01T00:35:00+08:00",
        "updated_at": "2026-05-01T00:35:00+08:00",
        "enabled": False,
        "dependencies": [],
        "config": {}
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        self.executed_count = 0
        self.error_count = 0
        
    @abstractmethod
    def initialize(self) -> bool:
        """初始化SKILL（子类必须实现）"""
        pass
    
    @abstractmethod
    def execute(self, data: Dict) -> Dict:
        """执行SKILL核心功能（子类必须实现）"""
        pass
    
    def validate(self, data: Dict) -> bool:
        """验证输入数据（子类可选重写）"""
        return bool(data)
    
    def get_metadata(self) -> Dict:
        """获取SKILL元数据（子类可选重写）"""
        return self.METADATA
    
    def get_status(self) -> Dict:
        """获取SKILL运行状态（子类可选重写）"""
        return {
            "status": "running" if self.initialized else "not_initialized",
            "metadata": self.get_metadata(),
            "executed_count": self.executed_count,
            "error_count": self.error_count,
            "last_execution": None,
            "config": self.config
        }
    
    def cleanup(self) -> bool:
        """清理SKILL资源（子类可选重写）"""
        try:
            self.initialized = False
            return True
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
            self.error_count += 1
            return False
    
    def _log_execution(self, data: Dict, result: Dict):
        """记录执行日志"""
        self.executed_count += 1
        if "error" in result:
            self.error_count += 1
            self.logger.error(f"执行失败: {result['error']}")
        else:
            self.logger.info(f"执行成功")
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        return {
            "executed_count": self.executed_count,
            "error_count": self.error_count,
            "success_rate": 1.0 - (self.error_count / self.executed_count if self.executed_count > 0 else 1),
            "avg_execution_time": 0.0  # 需要实现计时
        }
