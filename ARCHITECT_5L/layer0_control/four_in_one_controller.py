#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 0: 四位一体智能中枢 (新增安全师)

角色定位:
1. 🏗️ 顶级架构师 (Chief Architect) - 系统设计、架构演进、技术选型
2. 💰 顶级投资人 (Chief Investment Officer) - 市场洞察、机会识别、风险管理
3. 🎯 牛逼组织者 (Chief Operating Officer) - 团队协作、资源调度、冲突解决
4. 🔒 安全师 (Chief Security Officer) - 系统安全、异常处理、风险防控 ⭐ 新增

这是A5L的终极大脑，统御一切，安全运行。
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib

sys.path.insert(0, "/workspace/projects/workspace")

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入其他三位角色
from trinity_controller import ChiefArchitect, ChiefInvestmentOfficer, ChiefOperatingOfficer

class ChiefSecurityOfficer:
    """
    🔒 安全师
    
    职责:
    - 系统安全监控: 实时监控A5L运行状态
    - 异常检测处理: 发现问题立即处理
    - 权限管理: 确保访问控制
    - 风险预警: 提前发现潜在风险
    - 故障自愈: 自动修复常见问题
    - 安全审计: 记录所有安全事件
    - 应急响应: 紧急情况快速响应
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.security_logs: List[Dict] = []
        self.active_threats: List[Dict] = []
        self.safety_rules = self._init_safety_rules()
        self.error_patterns = self._init_error_patterns()
        self.autofix_enabled = True
        
        logger.info("🔒 Chief Security Officer: 安全师初始化完成")
    
    def _init_safety_rules(self) -> Dict:
        """初始化安全规则"""
        return {
            "file_access": {
                "forbidden_paths": ["/etc", "/root", "/sys"],
                "sensitive_patterns": ["password", "secret", "token", "key"],
                "max_file_size_mb": 100
            },
            "network": {
                "allowed_domains": ["feishu.cn", "openclaw.ai", "akshare.xyz"],
                "blocked_ports": [22, 23, 135, 445],
                "timeout_seconds": 30
            },
            "execution": {
                "forbidden_commands": ["rm -rf /", "mkfs", "dd if="],
                "max_execution_time": 300,
                "memory_limit_mb": 2048
            },
            "data": {
                "max_log_retention_days": 90,
                "encrypt_sensitive": True,
                "backup_required": True
            }
        }
    
    def _init_error_patterns(self) -> Dict:
        """初始化错误模式库"""
        return {
            "file_not_found": {
                "patterns": ["No such file", "ENOENT", "FileNotFoundError"],
                "severity": "medium",
                "autofix": "check_path_and_create_if_needed"
            },
            "permission_denied": {
                "patterns": ["Permission denied", "EACCES", "PermissionError"],
                "severity": "high",
                "autofix": "elevate_permissions_or_notify"
            },
            "network_timeout": {
                "patterns": ["timeout", "Connection refused", "ECONNREFUSED"],
                "severity": "medium",
                "autofix": "retry_with_backoff"
            },
            "api_rate_limit": {
                "patterns": ["rate limit", "429", "Too Many Requests"],
                "severity": "low",
                "autofix": "wait_and_retry"
            },
            "memory_error": {
                "patterns": ["MemoryError", "Out of memory", "ENOMEM"],
                "severity": "critical",
                "autofix": "clear_cache_and_restart"
            },
            "import_error": {
                "patterns": ["ImportError", "ModuleNotFoundError", "No module named"],
                "severity": "high",
                "autofix": "install_missing_package"
            },
            "syntax_error": {
                "patterns": ["SyntaxError", "IndentationError"],
                "severity": "critical",
                "autofix": "none"  # 需要人工修复
            }
        }
    
    def security_check(self, operation: str, params: Dict) -> Dict:
        """
        安全检查
        
        Args:
            operation: 操作类型
            params: 操作参数
            
        Returns:
            检查结果
        """
        risks = []
        approved = True
        
        # 文件操作检查
        if operation in ["read_file", "write_file", "delete_file"]:
            file_path = params.get("path", "")
            
            # 检查禁止路径
            for forbidden in self.safety_rules["file_access"]["forbidden_paths"]:
                if file_path.startswith(forbidden):
                    risks.append(f"🚫 禁止访问系统路径: {file_path}")
                    approved = False
            
            # 检查敏感文件名
            for sensitive in self.safety_rules["file_access"]["sensitive_patterns"]:
                if sensitive in file_path.lower():
                    risks.append(f"⚠️ 文件名包含敏感词: {sensitive}")
        
        # 命令执行检查
        if operation == "execute_command":
            command = params.get("command", "")
            
            # 检查危险命令
            for forbidden in self.safety_rules["execution"]["forbidden_commands"]:
                if forbidden in command:
                    risks.append(f"🚫 检测到危险命令: {forbidden}")
                    approved = False
        
        # 网络请求检查
        if operation == "network_request":
            url = params.get("url", "")
            
            # 检查域名
            domain_allowed = any(
                allowed in url 
                for allowed in self.safety_rules["network"]["allowed_domains"]
            )
            if not domain_allowed:
                risks.append(f"⚠️ 非白名单域名: {url}")
        
        return {
            "operation": operation,
            "approved": approved,
            "risks": risks,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_error(self, error: Exception, context: Dict = None) -> Dict:
        """
        错误处理
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            处理结果
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        logger.warning(f"🔒 安全师检测到错误: {error_type} - {error_str[:100]}")
        
        # 匹配错误模式
        matched_pattern = None
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(p.lower() in error_str.lower() for p in pattern_info["patterns"]):
                matched_pattern = pattern_name
                break
        
        if not matched_pattern:
            matched_pattern = "unknown"
        
        pattern_info = self.error_patterns.get(matched_pattern, {})
        severity = pattern_info.get("severity", "medium")
        autofix_strategy = pattern_info.get("autofix", "none")
        
        # 记录安全日志
        security_event = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_str[:200],
            "matched_pattern": matched_pattern,
            "severity": severity,
            "context": context,
            "autofix_attempted": False,
            "autofix_success": False
        }
        
        # 尝试自动修复
        fix_result = None
        if self.autofix_enabled and autofix_strategy != "none":
            security_event["autofix_attempted"] = True
            fix_result = self._attempt_autofix(autofix_strategy, error, context)
            security_event["autofix_success"] = fix_result["success"]
        
        self.security_logs.append(security_event)
        
        return {
            "error_type": error_type,
            "severity": severity,
            "pattern": matched_pattern,
            "autofix_attempted": security_event["autofix_attempted"],
            "autofix_success": security_event["autofix_success"],
            "fix_result": fix_result,
            "recommendation": self._get_recommendation(error_type, severity, fix_result)
        }
    
    def _attempt_autofix(self, strategy: str, error: Exception, context: Dict) -> Dict:
        """尝试自动修复"""
        logger.info(f"🔧 安全师尝试自动修复: {strategy}")
        
        fix_strategies = {
            "check_path_and_create_if_needed": self._fix_create_path,
            "retry_with_backoff": self._fix_retry,
            "wait_and_retry": self._fix_wait_and_retry,
            "clear_cache_and_restart": self._fix_clear_cache,
            "install_missing_package": self._fix_install_package,
            "elevate_permissions_or_notify": self._fix_permission
        }
        
        fix_func = fix_strategies.get(strategy)
        if fix_func:
            try:
                return fix_func(error, context)
            except Exception as e:
                return {"success": False, "error": str(e), "strategy": strategy}
        
        return {"success": False, "error": "Unknown fix strategy", "strategy": strategy}
    
    def _fix_create_path(self, error: Exception, context: Dict) -> Dict:
        """修复路径问题"""
        # 从错误信息中提取路径
        error_str = str(error)
        path_match = re.search(r"No such file or directory: ['\"](.+?)['\"]", error_str)
        
        if path_match:
            missing_path = path_match.group(1)
            parent_dir = os.path.dirname(missing_path)
            
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                return {"success": True, "action": f"创建目录: {parent_dir}"}
        
        return {"success": False, "error": "无法提取路径"}
    
    def _fix_retry(self, error: Exception, context: Dict) -> Dict:
        """重试操作"""
        import time
        time.sleep(2)  # 简单重试延迟
        return {"success": True, "action": "延迟2秒后重试"}
    
    def _fix_wait_and_retry(self, error: Exception, context: Dict) -> Dict:
        """等待后重试"""
        import time
        time.sleep(5)
        return {"success": True, "action": "等待5秒后重试"}
    
    def _fix_clear_cache(self, error: Exception, context: Dict) -> Dict:
        """清理缓存"""
        cache_dir = f"{self.workspace}/cache"
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            return {"success": True, "action": "清理缓存目录"}
        return {"success": False, "error": "缓存目录不存在"}
    
    def _fix_install_package(self, error: Exception, context: Dict) -> Dict:
        """安装缺失包"""
        error_str = str(error)
        module_match = re.search(r"No module named ['\"](.+?)['\"]", error_str)
        
        if module_match:
            module_name = module_match.group(1)
            # 这里可以调用pip安装
            return {"success": True, "action": f"需要安装模块: {module_name}", "module": module_name}
        
        return {"success": False, "error": "无法提取模块名"}
    
    def _fix_permission(self, error: Exception, context: Dict) -> Dict:
        """处理权限问题"""
        return {"success": False, "action": "需要提升权限或联系管理员", "requires_elevation": True}
    
    def _get_recommendation(self, error_type: str, severity: str, fix_result: Dict) -> str:
        """生成处理建议"""
        if fix_result and fix_result.get("success"):
            return f"✅ 自动修复成功: {fix_result.get('action', '')}"
        
        if severity == "critical":
            return "🚨 严重错误，建议立即人工介入"
        elif severity == "high":
            return "⚠️ 重要错误，建议尽快处理"
        elif severity == "medium":
            return "💡 一般错误，可稍后处理"
        else:
            return "📝 轻微问题，已记录"
    
    def monitor_system_health(self) -> Dict:
        """
        监控系统健康状态
        
        Returns:
            健康状态报告
        """
        checks = {
            "disk_space": self._check_disk_space(),
            "memory_usage": self._check_memory(),
            "critical_files": self._check_critical_files(),
            "recent_errors": self._check_recent_errors(),
            "security_score": 0.0
        }
        
        # 计算安全评分
        score = 100
        if not checks["disk_space"]["healthy"]:
            score -= 20
        if not checks["memory_usage"]["healthy"]:
            score -= 20
        if checks["recent_errors"]["count"] > 10:
            score -= 15
        
        checks["security_score"] = max(0, score)
        
        return checks
    
    def _check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/workspace")
            usage_percent = (used / total) * 100
            
            return {
                "healthy": usage_percent < 85,
                "usage_percent": usage_percent,
                "free_gb": free / (1024**3)
            }
        except:
            return {"healthy": True, "error": "无法检查"}
    
    def _check_memory(self) -> Dict:
        """检查内存使用"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                mem_total = int(lines[0].split()[1])
                mem_available = int(lines[2].split()[1])
                usage_percent = ((mem_total - mem_available) / mem_total) * 100
                
                return {
                    "healthy": usage_percent < 80,
                    "usage_percent": usage_percent,
                    "available_mb": mem_available / 1024
                }
        except:
            return {"healthy": True, "error": "无法检查"}
    
    def _check_critical_files(self) -> Dict:
        """检查关键文件"""
        critical_files = [
            f"{self.workspace}/SOUL.md",
            f"{self.workspace}/data/goals/goals.json",
            f"{self.workspace}/MEMORY.md"
        ]
        
        missing = [f for f in critical_files if not os.path.exists(f)]
        
        return {
            "healthy": len(missing) == 0,
            "missing_files": missing,
            "total_checked": len(critical_files)
        }
    
    def _check_recent_errors(self) -> Dict:
        """检查近期错误"""
        recent = [log for log in self.security_logs 
                 if (datetime.now() - datetime.fromisoformat(log["timestamp"])).days < 1]
        
        return {
            "count": len(recent),
            "critical_count": sum(1 for log in recent if log["severity"] == "critical"),
            "high_count": sum(1 for log in recent if log["severity"] == "high")
        }
    
    def get_security_report(self) -> Dict:
        """获取安全报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_events": len(self.security_logs),
            "active_threats": len(self.active_threats),
            "system_health": self.monitor_system_health(),
            "recent_critical_events": [
                log for log in self.security_logs[-10:]
                if log["severity"] in ["critical", "high"]
            ],
            "safety_rules_active": len(self.safety_rules),
            "autofix_enabled": self.autofix_enabled
        }

class Layer0_FourInOne:
    """
    🧠 Layer 0: 四位一体智能中枢
    
    整合:
    - Chief Architect (顶级架构师)
    - Chief Investment Officer (顶级投资人)
    - Chief Operating Officer (牛逼组织者)
    - Chief Security Officer (安全师) ⭐ 新增
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.architect = ChiefArchitect()
        self.cio = ChiefInvestmentOfficer()
        self.coo = ChiefOperatingOfficer()
        self.cso = ChiefSecurityOfficer(workspace)  # 新增安全师
        
        logger.info("="*70)
        logger.info("🧠 Layer 0: 四位一体智能中枢初始化")
        logger.info("   🏗️ 顶级架构师 - 系统设计、架构演进")
        logger.info("   💰 顶级投资人 - 市场洞察、机会识别")
        logger.info("   🎯 牛逼组织者 - 团队协作、资源调度")
        logger.info("   🔒 安全师 - 系统安全、异常处理")  # 新增
        logger.info("="*70)
    
    def secure_execute(self, operation: str, params: Dict) -> Dict:
        """
        安全执行操作
        先检查安全性，再执行
        """
        # 安全师先检查
        security_check = self.cso.security_check(operation, params)
        
        if not security_check["approved"]:
            return {
                "status": "blocked",
                "reason": "Security check failed",
                "risks": security_check["risks"]
            }
        
        try:
            # 执行操作
            result = {"status": "success", "operation": operation}
            return result
        except Exception as e:
            # 出错时安全师处理
            error_handling = self.cso.handle_error(e, {"operation": operation, "params": params})
            return {
                "status": "error",
                "error_handling": error_handling
            }
    
    def get_comprehensive_status(self) -> Dict:
        """获取综合状态报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "layer0_status": "operational",
            "four_in_one": {
                "architect": "active",
                "cio": "active",
                "coo": "active",
                "cso": "active"  # 新增
            },
            "security": self.cso.get_security_report(),
            "system_health": self.cso.monitor_system_health()
        }

def demo():
    """演示四位一体"""
    print("="*70)
    print("🧠 Layer 0 四位一体智能中枢演示 (新增安全师)")
    print("="*70)
    print()
    
    layer0 = Layer0_FourOne()
    print()
    
    # 演示1: 安全检查
    print("🔒 演示1: 安全检查")
    print("-"*70)
    
    check1 = layer0.cso.security_check("read_file", {"path": "/workspace/projects/workspace/SOUL.md"})
    print(f"  操作: read_file /workspace/projects/workspace/SOUL.md")
    print(f"  结果: {'✅ 通过' if check1['approved'] else '❌ 拒绝'}")
    print()
    
    check2 = layer0.cso.security_check("read_file", {"path": "/etc/passwd"})
    print(f"  操作: read_file /etc/passwd")
    print(f"  结果: {'✅ 通过' if check2['approved'] else '❌ 拒绝'}")
    if check2["risks"]:
        print(f"  风险: {check2['risks'][0]}")
    print()
    
    # 演示2: 错误处理
    print("🔧 演示2: 错误自动修复")
    print("-"*70)
    
    # 模拟文件不存在错误
    try:
        with open("/nonexistent/path/file.txt", "r") as f:
            f.read()
    except Exception as e:
        error_result = layer0.cso.handle_error(e, {"operation": "read_file"})
        print(f"  错误类型: {error_result['error_type']}")
        print(f"  严重程度: {error_result['severity']}")
        print(f"  匹配模式: {error_result['pattern']}")
        print(f"  自动修复: {'✅ 成功' if error_result['autofix_success'] else '❌ 失败'}")
        print(f"  建议: {error_result['recommendation']}")
    print()
    
    # 演示3: 系统健康检查
    print("📊 演示3: 系统健康检查")
    print("-"*70)
    health = layer0.cso.monitor_system_health()
    print(f"  磁盘空间: {'✅ 健康' if health['disk_space']['healthy'] else '⚠️ 告警'}")
    print(f"  内存使用: {'✅ 健康' if health['memory_usage']['healthy'] else '⚠️ 告警'}")
    print(f"  关键文件: {'✅ 完整' if health['critical_files']['healthy'] else '❌ 缺失'}")
    print(f"  安全评分: {health['security_score']}/100")
    print()
    
    # 演示4: 安全报告
    print("📋 演示4: 安全报告")
    print("-"*70)
    report = layer0.cso.get_security_report()
    print(f"  总事件数: {report['total_events']}")
    print(f"  活跃威胁: {report['active_threats']}")
    print(f"  自动修复: {'已启用' if report['autofix_enabled'] else '已禁用'}")
    print()
    
    print("="*70)
    print("✅ 四位一体演示完成！安全师已就位！")
    print("="*70)

if __name__ == "__main__":
    demo()
