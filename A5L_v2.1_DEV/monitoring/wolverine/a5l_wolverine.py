#!/usr/bin/env python3
"""
A5L Wolverine 自愈修复系统
集成Wolverine实现Python代码自动修复

使用GPT-4自动修复运行时的Python错误
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class A5LWolverine:
    """
    A5L Wolverine 自愈修复器
    自动检测和修复Python运行时错误
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.log_file = f"{workspace}/logs/wolverine_fixes.json"
        self.fix_history = []
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # 加载历史修复记录
        self._load_history()
    
    def _load_history(self):
        """加载修复历史"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                self.fix_history = json.load(f)
    
    def _save_history(self):
        """保存修复历史"""
        with open(self.log_file, 'w') as f:
            json.dump(self.fix_history, f, indent=2, ensure_ascii=False)
    
    def check_wolverine_installed(self) -> bool:
        """检查Wolverine是否安装"""
        try:
            result = subprocess.run(
                ["pip", "show", "wolverine"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def install_wolverine(self):
        """安装Wolverine"""
        print("📦 安装 Wolverine...")
        subprocess.run(
            ["pip", "install", "wolverine"],
            check=True
        )
        print("✅ Wolverine 安装完成")
    
    def fix_script(self, script_path: str, args: List[str] = None) -> Dict:
        """
        使用Wolverine修复Python脚本
        
        Args:
            script_path: Python脚本路径
            args: 脚本参数
            
        Returns:
            修复结果
        """
        if not self.check_wolverine_installed():
            self.install_wolverine()
        
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"脚本不存在: {script_path}",
                "timestamp": datetime.now().isoformat()
            }
        
        # 构建Wolverine命令
        cmd = ["wolverine", script_path]
        if args:
            cmd.extend(args)
        
        print(f"🔧 尝试修复: {script_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.workspace
            )
            
            fix_result = {
                "script": script_path,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            # 记录到历史
            self.fix_history.append(fix_result)
            self._save_history()
            
            if fix_result["success"]:
                print(f"✅ 修复成功: {script_path}")
            else:
                print(f"❌ 修复失败: {script_path}")
                print(f"   错误: {result.stderr[:200]}")
            
            return fix_result
            
        except subprocess.TimeoutExpired:
            return {
                "script": script_path,
                "success": False,
                "error": "修复超时(120秒)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "script": script_path,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def auto_fix_common_errors(self):
        """自动修复常见的A5L脚本错误"""
        scripts_to_fix = [
            "tools/finnhub_client.py",
            "data/simulation/update_trading_plan_docs.py",
            "tools/unified_data_source_manager.py"
        ]
        
        results = []
        for script in scripts_to_fix:
            script_path = os.path.join(self.workspace, script)
            if os.path.exists(script_path):
                result = self.fix_script(script_path)
                results.append(result)
        
        return results
    
    def get_fix_statistics(self) -> Dict:
        """获取修复统计"""
        total = len(self.fix_history)
        success = len([f for f in self.fix_history if f.get("success")])
        failed = total - success
        
        return {
            "total_fixes": total,
            "success": success,
            "failed": failed,
            "success_rate": success / total if total > 0 else 0,
            "recent_fixes": self.fix_history[-10:]  # 最近10次
        }
    
    def generate_report(self) -> str:
        """生成修复报告"""
        stats = self.get_fix_statistics()
        
        report = f"""
# A5L Wolverine 自愈修复报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 修复统计

| 指标 | 数值 |
|:-----|:-----|
| 总修复次数 | {stats['total_fixes']} |
| 成功次数 | {stats['success']} |
| 失败次数 | {stats['failed']} |
| 成功率 | {stats['success_rate']*100:.1f}% |

## 最近修复记录

"""
        for fix in stats['recent_fixes']:
            status = "✅" if fix.get("success") else "❌"
            report += f"- {status} {fix['script']} ({fix['timestamp'][:10]})\n"
        
        return report


def main():
    """主函数 - 演示Wolverine自愈修复"""
    print("=" * 70)
    print("🔧 A5L Wolverine 自愈修复系统")
    print("=" * 70)
    
    wolverine = A5LWolverine()
    
    # 检查安装
    if not wolverine.check_wolverine_installed():
        print("⚠️ Wolverine 未安装，正在安装...")
        wolverine.install_wolverine()
    else:
        print("✅ Wolverine 已安装")
    
    # 显示统计
    print("\n📊 修复统计:")
    stats = wolverine.get_fix_statistics()
    print(f"   总修复次数: {stats['total_fixes']}")
    print(f"   成功率: {stats['success_rate']*100:.1f}%")
    
    # 自动修复常见脚本
    print("\n🔧 自动修复常见脚本...")
    results = wolverine.auto_fix_common_errors()
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['script']}")
    
    print("\n" + "=" * 70)
    print("✅ Wolverine 系统就绪!")
    print("=" * 70)
    print("\n使用方法:")
    print("  from monitoring.wolverine.a5l_wolverine import A5LWolverine")
    print("  w = A5LWolverine()")
    print("  w.fix_script('path/to/script.py')")


if __name__ == "__main__":
    main()
