#!/usr/bin/env python3
"""
LS Factor Monitor - 流动性压力因子监控
监控市场流动性指标、信用利差、VIX等压力信号
"""

import json
import os
from datetime import datetime, timedelta
import argparse

def get_mock_ls_data():
    """获取流动性压力数据（模拟版本）"""
    return {
        "date": (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d"),
        "liquidity_stress_index": 45.2,
        "level": "moderate",
        "indicators": {
            "vix": {
                "value": 18.5,
                "signal": "normal",
                "description": "恐慌指数正常范围"
            },
            "credit_spread": {
                "value": 125,
                "signal": "normal",
                "description": "信用利差处于历史均值"
            },
            "ted_spread": {
                "value": 0.35,
                "signal": "low",
                "description": "银行间流动性充裕"
            },
            "liquidity_premium": {
                "value": 0.8,
                "signal": "low",
                "description": "流动性溢价较低"
            }
        },
        "risk_signals": [
            {
                "type": "warning",
                "message": "美债收益率曲线扁平化，关注衰退信号",
                "severity": "medium"
            }
        ],
        "outlook": "短期流动性环境相对稳定，但需关注美联储缩表进程和银行准备金变化",
        "timestamp": (datetime.utcnow() + timedelta(hours=8)).isoformat()
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-only', action='store_true', help='仅输出到文件，不发送消息')
    args = parser.parse_args()
    
    # 获取数据
    data = get_mock_ls_data()
    
    # 确保目录存在
    os.makedirs('/workspace/projects/workspace/data/macro', exist_ok=True)
    
    # 生成文件名
    date_str = data['date'].replace('-', '')
    output_file = f'/workspace/projects/workspace/data/macro/ls_{date_str}.json'
    
    # 保存JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 打印报告
    print("=" * 60)
    print("💧 LS FACTOR MONITOR - 流动性压力监控")
    print(f"📅 {data['date']}")
    print("=" * 60)
    print()
    print(f"📊 流动性压力指数: {data['liquidity_stress_index']}")
    print(f"📈 压力等级: {data['level']}")
    print()
    print("📋 关键指标:")
    for name, indicator in data['indicators'].items():
        print(f"  • {name}: {indicator['value']} ({indicator['signal']})")
        print(f"    {indicator['description']}")
    print()
    print("⚠️ 风险信号:")
    for signal in data['risk_signals']:
        print(f"  • [{signal['severity']}] {signal['message']}")
    print()
    print(f"📝 展望: {data['outlook']}")
    print()
    print(f"✅ 数据已保存: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
