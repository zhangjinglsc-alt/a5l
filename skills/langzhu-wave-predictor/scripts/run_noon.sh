#!/bin/bash
# 浪主预测系统 - 午盘脚本（验证+下午预测）
# 运行时间: 中午11:35

cd /workspace/projects/workspace

echo "========================================"
echo "🌊 浪主波浪理论 - 午盘验证+下午预测"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

echo ""
echo "📊 步骤1: 验证早盘预测..."
python3 skills/langzhu-wave-predictor/scripts/predictor.py verify --session morning

echo ""
echo "📈 步骤2: 下午预测..."
python3 skills/langzhu-wave-predictor/scripts/predictor.py predict --session afternoon --index sh000001

echo ""
echo "✅ 午盘任务完成"
