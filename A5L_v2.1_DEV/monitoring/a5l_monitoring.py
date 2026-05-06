#!/usr/bin/env python3
"""
A5L P0监控系统主入口
一键启动所有监控组件
"""

import os
import sys
import subprocess
import time
from datetime import datetime

class A5LMonitoringSystem:
    """
    A5L 监控系统主控制器
    """
    
    def __init__(self):
        self.workspace = "/workspace/projects/workspace"
        self.components = {
            "error_classifier": {
                "status": "ready",
                "file": "monitoring/wolverine/error_classifier.py",
                "description": "错误自动分类器"
            },
            "healing_executor": {
                "status": "ready",
                "file": "monitoring/wolverine/healing_executor.py",
                "description": "自动化修复执行器"
            },
            "fault_warning": {
                "status": "ready",
                "file": "monitoring/wolverine/fault_warning_system.py",
                "description": "故障预警系统"
            },
            "prometheus": {
                "status": "config_ready",
                "file": "monitoring/prometheus/prometheus.yml",
                "description": "Prometheus监控",
                "note": "需要手动启动Prometheus服务"
            },
            "upptime": {
                "status": "config_ready",
                "file": "monitoring/upptime/.upptimerc.yml",
                "description": "Upptime状态监控",
                "note": "需要在GitHub创建独立仓库"
            }
        }
    
    def check_status(self):
        """检查所有组件状态"""
        print("=" * 70)
        print("📊 A5L P0监控系统状态")
        print("=" * 70)
        
        for name, info in self.components.items():
            status_icon = "✅" if "ready" in info["status"] else "⚠️"
            print(f"\n{status_icon} {name}")
            print(f"   描述: {info['description']}")
            print(f"   状态: {info['status']}")
            if "note" in info:
                print(f"   注意: {info['note']}")
    
    def test_wolverine(self):
        """测试Wolverine自愈系统"""
        print("\n" + "=" * 70)
        print("🩹 测试Wolverine自愈系统")
        print("=" * 70)
        
        sys.path.insert(0, f"{self.workspace}/monitoring/wolverine")
        from fault_warning_system import FaultWarningSystem
        
        system = FaultWarningSystem()
        
        # 模拟处理错误
        test_errors = [
            "Yahoo Finance API error: Too Many Requests",
            "MemoryError: Unable to allocate",
            "feishu API error: forbidden, code: 1770032"
        ]
        
        for error in test_errors:
            print(f"\n处理: {error[:50]}...")
            result = system.process_error(error)
            print(f"   → {result['classification']['error_type']}: " +
                  f"{'✅自愈' if result['healing'] and result['healing']['success'] else '⏭️跳过'}")
        
        # 生成报告
        report = system.generate_report()
        print("\n" + report)
    
    def start_prometheus(self):
        """启动Prometheus (如果已安装)"""
        print("\n" + "=" * 70)
        print("📈 启动Prometheus")
        print("=" * 70)
        
        # 检查是否已安装
        result = subprocess.run(
            ["which", "prometheus"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("⚠️ Prometheus未安装")
            print("\n安装命令:")
            print("  wget https://github.com/prometheus/prometheus/releases/download/...")
            print("  tar xzf prometheus-*.tar.gz")
            print("  sudo mv prometheus /usr/local/bin/")
            return False
        
        # 启动Prometheus
        print("✅ Prometheus已安装")
        print("\n启动命令:")
        print(f"  prometheus --config.file={self.workspace}/monitoring/prometheus/prometheus.yml")
        print("\n访问: http://localhost:9090")
        
        return True
    
    def setup_upptime(self):
        """显示Upptime设置指南"""
        print("\n" + "=" * 70)
        print("⏱️  Upptime设置指南")
        print("=" * 70)
        
        print("\n步骤1: 在GitHub创建新仓库")
        print("  名称: a5l-upptime")
        print("  类型: Public")
        
        print("\n步骤2: 复制配置文件")
        print(f"  cd ~/a5l-upptime")
        print(f"  cp {self.workspace}/monitoring/upptime/* .")
        
        print("\n步骤3: 设置GitHub Secrets")
        print("  Settings → Secrets → New repository secret")
        print("  GH_PAT: [你的GitHub Personal Access Token]")
        print("  FEISHU_WEBHOOK_URL: [飞书机器人Webhook]")
        
        print("\n步骤4: 启用Actions并推送")
        print("  git add .")
        print("  git commit -m 'Initial Upptime config'")
        print("  git push origin main")
        
        print("\n步骤5: 访问状态页面")
        print("  https://[你的用户名].github.io/a5l-upptime")
    
    def generate_report(self):
        """生成完整报告"""
        print("\n" + "=" * 70)
        print("📋 A5L P0监控系统部署报告")
        print("=" * 70)
        print(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n## 已部署组件")
        print("\n✅ 自愈系统 (Wolverine)")
        print("  - error_classifier.py: 错误自动分类器")
        print("  - healing_executor.py: 自动化修复执行器")
        print("  - fault_warning_system.py: 故障预警系统")
        
        print("\n⚠️  待手动配置")
        print("  - Prometheus: 需要安装并启动")
        print("  - Upptime: 需要在GitHub创建仓库")
        print("  - Alertmanager: 需要配置飞书Webhook")
        
        print("\n## 自愈能力")
        print("\n已实现的自愈规则:")
        print("  1. yahoo_rate_limit → 自动切换Finnhub")
        print("  2. memory_error → 清理缓存")
        print("  3. position_data_corrupt → 从备份恢复")
        print("  4. github_push_failed → 延时重试")
        print("  5. feishu_doc_update_failed → 标记重新创建")
        print("  6. api_key_invalid → 请求轮换API Key")
        
        print("\n## 下一步")
        print("  1. 安装Prometheus并启动")
        print("  2. 创建GitHub仓库配置Upptime")
        print("  3. 配置飞书Webhook")
        print("  4. 测试告警通知")


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 A5L P0监控系统 - 主入口")
    print("=" * 70)
    
    system = A5LMonitoringSystem()
    
    if len(sys.argv) < 2:
        print("\n用法: python3 a5l_monitoring.py [命令]")
        print("\n命令:")
        print("  status      - 检查所有组件状态")
        print("  test        - 测试自愈系统")
        print("  prometheus  - 启动Prometheus指南")
        print("  upptime     - Upptime设置指南")
        print("  report      - 生成部署报告")
        print("  all         - 执行所有检查")
        print("")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        system.check_status()
    elif command == "test":
        system.test_wolverine()
    elif command == "prometheus":
        system.start_prometheus()
    elif command == "upptime":
        system.setup_upptime()
    elif command == "report":
        system.generate_report()
    elif command == "all":
        system.check_status()
        system.test_wolverine()
        system.generate_report()
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ 完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
