#!/usr/bin/env python3
"""
A5L 系统健康检查脚本
Alpha测试前全面检查
"""

import os
import sys
import json
from datetime import datetime

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """检查目录是否存在"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists

def run_health_check():
    """运行健康检查"""
    print("=" * 70)
    print("🩺 A5L 系统健康检查")
    print("=" * 70)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    checks = []
    
    # 1. 检查核心模块
    print("\n【1】核心模块检查")
    print("-" * 70)
    core_modules = [
        ("data/architect_5l/backtest_engine.py", "回测引擎"),
        ("data/architect_5l/risk_manager.py", "风控系统"),
        ("data/architect_5l/broker_api.py", "券商API"),
        ("data/architect_5l/ml_prediction_engine.py", "ML预测"),
        ("data/architect_5l/multi_strategy_engine.py", "多策略引擎"),
        ("data/architect_5l/position_manager.py", "仓位管理"),
        ("data/architect_5l/execution_optimizer.py", "执行优化"),
    ]
    for filepath, desc in core_modules:
        checks.append(check_file_exists(filepath, desc))
    
    # 2. 检查数据目录
    print("\n【2】数据目录检查")
    print("-" * 70)
    data_dirs = [
        ("data/positions", "持仓数据"),
        ("data/simulation", "模拟交易"),
        ("data/architect_5l/signals", "信号数据"),
        ("data/architect_5l/incidents", "事故记录"),
    ]
    for dirpath, desc in data_dirs:
        checks.append(check_directory_exists(dirpath, desc))
    
    # 3. 检查配置文件
    print("\n【3】配置文件检查")
    print("-" * 70)
    config_files = [
        ("A5L_v4_SUMMARY.md", "项目总结"),
        ("ALPHA_TEST_PLAN.md", "测试计划"),
        ("deploy.sh", "部署脚本"),
    ]
    for filepath, desc in config_files:
        checks.append(check_file_exists(filepath, desc))
    
    # 4. 检查持仓数据
    print("\n【4】持仓数据检查")
    print("-" * 70)
    position_file = "data/positions/position_summary.json"
    if os.path.exists(position_file):
        try:
            with open(position_file, 'r') as f:
                positions = json.load(f)
            print(f"✅ 持仓数据正常")
            print(f"   持仓数量: {positions.get('positions_count', 0)}只")
            print(f"   总资产: ¥{positions.get('total_value', 0):,.2f}")
            checks.append(True)
        except Exception as e:
            print(f"❌ 持仓数据异常: {e}")
            checks.append(False)
    else:
        print(f"⚠️  持仓数据文件不存在")
        checks.append(False)
    
    # 5. 检查Git状态
    print("\n【5】Git状态检查")
    print("-" * 70)
    git_dir = ".git"
    if os.path.isdir(git_dir):
        print(f"✅ Git仓库正常")
        checks.append(True)
    else:
        print(f"❌ Git仓库异常")
        checks.append(False)
    
    # 汇总
    print("\n" + "=" * 70)
    print("📊 检查结果汇总")
    print("=" * 70)
    passed = sum(checks)
    total = len(checks)
    score = passed / total * 100 if total > 0 else 0
    
    print(f"通过检查: {passed}/{total}")
    print(f"健康评分: {score:.1f}/100")
    
    if score >= 90:
        print("🟢 系统健康，可以开始Alpha测试")
    elif score >= 70:
        print("🟡 系统基本正常，建议修复警告项后测试")
    else:
        print("🔴 系统异常，请先修复问题")
    
    print("=" * 70)
    
    return score

if __name__ == "__main__":
    score = run_health_check()
    sys.exit(0 if score >= 70 else 1)
