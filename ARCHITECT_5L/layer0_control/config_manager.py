#!/usr/bin/env python3
"""
A5L 配置管理器
支持: YAML配置、环境变量、多环境切换
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class A5LConfig:
    """A5L统一配置管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = None):
        if self._initialized:
            return
            
        self.config_path = config_path or self._find_config()
        self._config = {}
        self._load_config()
        self._apply_env_overrides()
        self._initialized = True
    
    def _find_config(self) -> str:
        """查找配置文件"""
        possible_paths = [
            "./config/a5l_config.yaml",
            "../config/a5l_config.yaml",
            "/workspace/projects/workspace/config/a5l_config.yaml",
            os.path.expanduser("~/.a5l/config.yaml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Config file not found")
    
    def _load_config(self):
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        print(f"✅ Config loaded from {self.config_path}")
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        env_mappings = {
            'A5L_ENV': ['system', 'environment'],
            'A5L_DEBUG': ['system', 'debug'],
            'A5L_LOG_LEVEL': ['system', 'log_level'],
            'A5L_FEISHU_TOKEN': ['services', 'feishu', 'folder_token'],
            'A5L_DATA_PATH': ['paths', 'data'],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(self._config, config_path, value)
                print(f"🔧 Override from env: {env_var}")
    
    def _set_nested_value(self, d: dict, path: list, value: Any):
        """设置嵌套值"""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value
    
    def get(self, *path: str, default: Any = None) -> Any:
        """获取配置值"""
        value = self._config
        for key in path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_system(self, key: str) -> Any:
        """获取系统配置"""
        return self.get('system', key)
    
    def get_data_config(self) -> Dict:
        """获取数据层配置"""
        return self.get('data') or {}
    
    def get_strategy_config(self) -> Dict:
        """获取策略层配置"""
        return self.get('strategy') or {}
    
    def get_analysis_config(self) -> Dict:
        """获取分析层配置"""
        return self.get('analysis') or {}
    
    def get_execution_config(self) -> Dict:
        """获取执行层配置"""
        return self.get('execution') or {}
    
    def get_learning_config(self) -> Dict:
        """获取学习层配置"""
        return self.get('learning') or {}
    
    def get_integration_config(self) -> Dict:
        """获取整合引擎配置"""
        return self.get('integration') or {}
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        # 检查各层配置
        for layer in ['data', 'strategy', 'analysis', 'execution', 'learning', 'integration']:
            layer_config = self.get(layer)
            if layer_config and feature in layer_config:
                if isinstance(layer_config[feature], dict):
                    return layer_config[feature].get('enabled', False)
        return False
    
    def reload(self):
        """重新加载配置"""
        self._load_config()
        self._apply_env_overrides()
        print("🔄 Config reloaded")
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return self._config.copy()


# 全局配置实例
config = A5LConfig()


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 A5L Configuration Manager")
    print("=" * 60)
    print()
    
    # 显示系统配置
    print("📊 System Config:")
    print(f"  Name: {config.get_system('name')}")
    print(f"  Version: {config.get_system('version')}")
    print(f"  Environment: {config.get_system('environment')}")
    print(f"  Debug: {config.get_system('debug')}")
    print()
    
    # 显示数据源配置
    print("📡 Data Sources:")
    data_config = config.get_data_config()
    print(f"  Primary: {data_config.get('sources', {}).get('primary')}")
    print(f"  Backups: {data_config.get('sources', {}).get('backups')}")
    print()
    
    # 显示功能开关
    print("🔧 Feature Flags:")
    features = [
        'quality', 'sandbox', 'bias_detection', 
        'risk_control', 'review', 'adaptive_routing'
    ]
    for feature in features:
        enabled = config.is_feature_enabled(feature)
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
    print()
    
    print("=" * 60)
    print("✅ Configuration Manager Ready!")
    print("=" * 60)
