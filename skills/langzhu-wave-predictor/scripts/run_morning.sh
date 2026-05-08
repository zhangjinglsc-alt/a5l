#!/bin/bash
# 浪主预测系统 - 早盘预测脚本
# 运行时间: 上午9:25

cd /workspace/projects/workspace

echo "========================================"
echo "🌊 浪主波浪理论 - 早盘预测"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 上证指数早盘预测
python3 skills/langzhu-wave-predictor/scripts/predictor.py predict --session morning --index sh000001

echo ""
echo "✅ 早盘预测完成"
