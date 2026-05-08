#!/bin/bash
# A5L SKILL自主学习脚本
# 每小时执行一次，从真实数据中学习

echo "🧠 A5L SKILL自主学习启动"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo "从飞书云文档 + 交易记录 + 市场数据中学习"
echo ""

cd /workspace/projects/workspace

# 执行自主学习
python3 TOOLS/autonomous_learning_system.py

# 更新Git
git add data/skill_knowledge_base.json data/autonomous_learning_log.json
git commit -m "learning: Autonomous learning session $(date '+%H%M') - from real data"
git push

echo ""
echo "=========================================="
echo "✅ 自主学习完成并推送至GitHub"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
