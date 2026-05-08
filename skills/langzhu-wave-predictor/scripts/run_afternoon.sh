#!/bin/bash
# 浪主预测系统 - 收盘验证脚本
# 运行时间: 下午15:05

cd /workspace/projects/workspace

echo "========================================"
echo "🌊 浪主波浪理论 - 收盘验证总结"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

echo ""
echo "📊 验证所有今日预测..."
python3 skills/langzhu-wave-predictor/scripts/predictor.py verify --session all

echo ""
echo "📈 生成今日总结报告..."
python3 skills/langzhu-wave-predictor/scripts/daily_summary.py

echo ""
echo "✅ 收盘验证完成"
