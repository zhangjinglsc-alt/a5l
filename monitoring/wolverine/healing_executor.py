#!/usr/bin/env python3
"""
A5L 自动化修复执行器
执行自愈规则和修复操作
"""

import os
import sys
import json
import time
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Callable

class HealingExecutor:
    """
    自动化修复执行器
    执行各种自愈操作
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.healing_log = f"{workspace}/logs/healing_actions.json"
        self.action_history = []
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.healing_log), exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """加载修复历史"""
        if os.path.exists(self.healing_log):
            try:
                with open(self.healing_log, 'r') as f:
                    self.action_history = json.load(f)
            except:
                self.action_history = []
    
    def _save_history(self):
        """保存修复历史"""
        with open(self.healing_log, 'w') as f:
            json.dump(self.action_history, f, indent=2, ensure_ascii=False)
    
    def execute_healing(self, error_type: str, context: Dict = None) -> Dict:
        """
        执行自愈操作
        
        Args:
            error_type: 错误类型
            context: 上下文信息
            
        Returns:
            执行结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "context": context or {},
            "success": False,
            "action": None,
            "message": ""
        }
        
        # 获取对应的修复方法
        method_name = f"_heal_{error_type}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                action_result = method(context)
                result.update(action_result)
            except Exception as e:
                result["message"] = f"修复执行异常: {str(e)}"
        else:
            result["message"] = f"未知的错误类型: {error_type}"
        
        # 记录历史
        self.action_history.append(result)
        self._save_history()
        
        return result
    
    # ===== 自愈方法 =====
    
    def _heal_yahoo_rate_limit(self, context: Dict) -> Dict:
        """Yahoo Finance限流 - 切换到Finnhub"""
        print("🔧 执行自愈: 切换到Finnhub数据源...")
        
        try:
            # 修改数据源配置
            config_path = f"{self.workspace}/config/data_source_priority.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # 将Finnhub设为首选
                config["priority"] = ["finnhub", "yahoo", "akshare"]
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                return {
                    "success": True,
                    "action": "switch_to_finnhub",
                    "message": "已将数据源切换到Finnhub"
                }
            else:
                # 创建新配置
                config = {"priority": ["finnhub", "yahoo", "akshare"]}
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                return {
                    "success": True,
                    "action": "create_and_switch",
                    "message": "创建配置并切换到Finnhub"
                }
        except Exception as e:
            return {
                "success": False,
                "action": "switch_to_finnhub",
                "message": f"切换失败: {str(e)}"
            }
    
    def _heal_memory_error(self, context: Dict) -> Dict:
        """内存不足 - 清理缓存"""
        print("🔧 执行自愈: 清理缓存...")
        
        cleared = []
        
        # 清理临时目录
        cache_dirs = [
            '/tmp/a5l_cache',
            '/tmp/openclaw',
            f"{self.workspace}/.cache"
        ]
        
        for d in cache_dirs:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                    cleared.append(d)
                except Exception as e:
                    print(f"   清理失败 {d}: {e}")
        
        # Python垃圾回收
        import gc
        gc.collect()
        
        return {
            "success": True,
            "action": "clear_cache",
            "message": f"已清理 {len(cleared)} 个缓存目录",
            "cleared_dirs": cleared
        }
    
    def _heal_position_data_corrupt(self, context: Dict) -> Dict:
        """持仓数据损坏 - 从备份恢复"""
        print("🔧 执行自愈: 从备份恢复持仓数据...")
        
        try:
            # 找到最新的备份
            backup_dir = f"{self.workspace}/archive"
            if not os.path.exists(backup_dir):
                return {
                    "success": False,
                    "action": "restore_from_backup",
                    "message": "备份目录不存在"
                }
            
            # 执行恢复脚本
            result = subprocess.run(
                ["python3", f"{self.workspace}/TOOLS/ssmg_restore.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "action": "restore_from_backup",
                "message": "备份恢复" + ("成功" if result.returncode == 0 else "失败"),
                "stdout": result.stdout[-500:] if result.stdout else ""
            }
        except Exception as e:
            return {
                "success": False,
                "action": "restore_from_backup",
                "message": f"恢复失败: {str(e)}"
            }
    
    def _heal_github_push_failed(self, context: Dict) -> Dict:
        """GitHub推送失败 - 延时重试"""
        print("🔧 执行自愈: 延时重试GitHub推送...")
        
        # 延时5秒后重试
        time.sleep(5)
        
        try:
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.workspace
            )
            
            return {
                "success": result.returncode == 0,
                "action": "retry_with_delay",
                "message": "推送" + ("成功" if result.returncode == 0 else "仍然失败"),
                "stdout": result.stdout[-200:] if result.stdout else ""
            }
        except Exception as e:
            return {
                "success": False,
                "action": "retry_with_delay",
                "message": f"重试失败: {str(e)}"
            }
    
    def _heal_feishu_doc_update_failed(self, context: Dict) -> Dict:
        """飞书文档更新失败 - 重新创建文档"""
        print("🔧 执行自愈: 重新创建飞书文档...")
        
        # 标记需要重新创建
        doc_id = context.get("doc_id", "unknown") if context else "unknown"
        
        # 记录到待处理列表
        pending_file = f"{self.workspace}/logs/feishu_docs_to_recreate.json"
        pending = []
        if os.path.exists(pending_file):
            with open(pending_file, 'r') as f:
                pending = json.load(f)
        
        pending.append({
            "doc_id": doc_id,
            "timestamp": datetime.now().isoformat(),
            "reason": "update_failed"
        })
        
        with open(pending_file, 'w') as f:
            json.dump(pending, f, indent=2)
        
        return {
            "success": True,
            "action": "mark_for_recreation",
            "message": f"已将文档 {doc_id} 标记为待重新创建"
        }
    
    def _heal_api_key_invalid(self, context: Dict) -> Dict:
        """API Key失效 - 轮换API Key"""
        print("🔧 执行自愈: 轮换API Key...")
        
        api_name = context.get("api_name", "unknown")
        
        # 记录轮换请求
        rotation_file = f"{self.workspace}/logs/api_key_rotation.json"
        rotation = []
        if os.path.exists(rotation_file):
            with open(rotation_file, 'r') as f:
                rotation = json.load(f)
        
        rotation.append({
            "api_name": api_name,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_manual"
        })
        
        with open(rotation_file, 'w') as f:
            json.dump(rotation, f, indent=2)
        
        return {
            "success": True,
            "action": "request_key_rotation",
            "message": f"已请求轮换 {api_name} 的API Key，需要人工确认"
        }
    
    def get_statistics(self) -> Dict:
        """获取修复统计"""
        if not self.action_history:
            return {"total": 0}
        
        total = len(self.action_history)
        success = len([a for a in self.action_history if a["success"]])
        
        # 按类型统计
        action_counts = {}
        for a in self.action_history:
            action = a.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_actions": total,
            "success": success,
            "failed": total - success,
            "success_rate": success / total if total > 0 else 0,
            "by_action": action_counts
        }


# 快速测试
if __name__ == "__main__":
    print("=" * 70)
    print("🩹 A5L 自动化修复执行器测试")
    print("=" * 70)
    
    executor = HealingExecutor()
    
    # 测试用例
    test_cases = [
        ("yahoo_rate_limit", {}),
        ("memory_error", {}),
        ("github_push_failed", {}),
        ("feishu_doc_update_failed", {"doc_id": "test123"}),
    ]
    
    print("\n测试自愈执行:\n")
    for error_type, context in test_cases:
        print(f"\n测试: {error_type}")
        result = executor.execute_healing(error_type, context)
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['action']}: {result['message']}")
    
    print("\n" + "=" * 70)
    print("📊 修复统计:")
    stats = executor.get_statistics()
    print(f"   总执行: {stats['total_actions']}")
    print(f"   成功: {stats['success']} ({stats['success_rate']*100:.1f}%)")
    print("=" * 70)
