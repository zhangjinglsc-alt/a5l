#!/bin/bash
# SSMG Session Startup Script
# SOUL-SKILL-MEMORY-GOAL 会话启动脚本
# 
# 这个脚本应该在每次Agent会话开始时执行
# 它会加载完整的四层架构上下文

echo "=================================="
echo "SSMG Session Startup"
echo "=================================="
echo ""

WORKSPACE="/workspace/projects/workspace"
cd "$WORKSPACE"

# 检查并运行SSMG初始化
if [ -f "TOOLS/ssmg_integration_engine.py" ]; then
    echo "🔧 Running SSMG Integration Engine..."
    python3 TOOLS/ssmg_integration_engine.py
    echo ""
    echo "✅ SSMG initialization complete"
else
    echo "⚠️  SSMG Integration Engine not found"
fi

echo ""
echo "=================================="
echo "Session Ready"
echo "=================================="
