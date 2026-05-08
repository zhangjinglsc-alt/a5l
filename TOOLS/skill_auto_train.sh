#!/bin/bash
# A5L SKILL自动训练脚本
# 每30分钟执行一次，持续训练新SKILL

echo "🚀 A5L SKILL自动训练启动"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

cd /workspace/projects/workspace

# 执行训练
python3 TOOLS/skill_training_system.py

# 更新Git
git add SKILL_REGISTRY.json data/skill_training_log.json
git commit -m "training: Auto skill training session $(date '+%H%M')"
git push

echo "=========================================="
echo "✅ 训练完成并推送至GitHub"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
