#!/usr/bin/env python3
"""
A5L 浪主预测系统 - 定时任务调度器
上午9:25预测 -> 中午11:35验证+下午预测 -> 下午15:05验证总结
"""

import json
from datetime import datetime
from pathlib import Path

CRON_CONFIG = {
    "name": "langzhu-wave-predictor",
    "version": "1.0.0",
    "description": "浪主波浪理论预测系统 - 一天两次预测验证循环",
    
    "schedule": {
        "morning_predict": {
            "time": "09:25",
            "description": "早盘开盘前预测",
            "action": "predict",
            "session": "morning",
            "enabled": True
        },
        "noon_verify_and_predict": {
            "time": "11:35",
            "description": "中午收盘验证+下午预测",
            "actions": ["verify_morning", "predict_afternoon"],
            "enabled": True
        },
        "afternoon_verify": {
            "time": "15:05",
            "description": "下午收盘验证总结",
            "action": "verify",
            "session": "all",
            "enabled": True
        }
    },
    
    "execution": {
        "script_path": "/workspace/projects/workspace/skills/langzhu-wave-predictor/scripts/predictor.py",
        "python": "python3",
        "log_dir": "/workspace/projects/workspace/skills/langzhu-wave-predictor/logs"
    },
    
    "indexes": [
        {"code": "sh000001", "name": "上证指数", "primary": True},
        {"code": "sz399001", "name": "深证成指", "primary": False},
        {"code": "sh000016", "name": "上证50", "primary": False}
    ]
}

def generate_cron_jobs():
    """生成cron任务配置"""
    
    jobs = []
    
    # 上午9:25预测
    jobs.append({
        "name": "langzhu-morning-predict",
        "schedule": "25 9 * * 1-5",  # 工作日9:25
        "command": f"cd /workspace/projects/workspace && python3 skills/langzhu-wave-predictor/scripts/run_morning.sh",
        "description": "浪主预测-早盘"
    })
    
    # 中午11:35验证+预测
    jobs.append({
        "name": "langzhu-noon-verify-predict",
        "schedule": "35 11 * * 1-5",  # 工作日11:35
        "command": f"cd /workspace/projects/workspace && python3 skills/langzhu-wave-predictor/scripts/run_noon.sh",
        "description": "浪主预测-午盘验证+下午预测"
    })
    
    # 下午15:05验证
    jobs.append({
        "name": "langzhu-afternoon-verify",
        "schedule": "5 15 * * 1-5",  # 工作日15:05
        "command": f"cd /workspace/projects/workspace && python3 skills/langzhu-wave-predictor/scripts/run_afternoon.sh",
        "description": "浪主预测-收盘验证"
    })
    
    return jobs

if __name__ == "__main__":
    # 保存配置
    config_path = Path("/workspace/projects/workspace/skills/langzhu-wave-predictor/config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(CRON_CONFIG, f, ensure_ascii=False, indent=2)
    
    # 生成cron任务
    jobs = generate_cron_jobs()
    
    print("="*70)
    print("浪主波浪理论预测系统 - 定时任务配置".center(60))
    print("="*70)
    
    print("\n📅 任务调度:")
    for job in jobs:
        print(f"\n  {job['name']}")
        print(f"    时间: {job['schedule']}")
        print(f"    描述: {job['description']}")
        print(f"    命令: {job['command']}")
    
    print("\n\n🔧 配置已保存:")
    print(f"  {config_path}")
    
    print("\n\n📋 添加到cron的步骤:")
    print("  1. crontab -e")
    print("  2. 添加上面的3个任务")
    print("  3. 或使用OpenClaw cron工具自动添加")
