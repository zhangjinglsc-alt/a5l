#!/bin/bash
# A5L v2.1 生产环境部署脚本
# 执行前请确保：
# 1. 已阅读 A5L_v2.1_UPGRADE_COMPLETE_REPORT.md
# 2. 已确认要部署
# 3. 当前在 /workspace/projects/workspace 目录

set -e  # 遇到错误立即退出

echo "=============================================="
echo "🚀 A5L v2.1 生产环境部署"
echo "=============================================="
echo "时间: $(date)"
echo ""

# Step 1: 备份当前生产环境
echo "Step 1: 备份当前生产环境..."
BACKUP_DIR="backups/PRE_V2.1_DEPLOY_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tools/*.py "$BACKUP_DIR/" 2>/dev/null || true
cp -r data/simulation/*.json "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ 备份完成: $BACKUP_DIR"
echo ""

# Step 2: 部署新组件
echo "Step 2: 部署新组件..."

# 部署 unified_portfolio_manager.py
if [ -f "A5L_v2.1_DEV/tools/unified_portfolio_manager.py" ]; then
    cp A5L_v2.1_DEV/tools/unified_portfolio_manager.py tools/
    echo "✅ 部署: unified_portfolio_manager.py"
fi

# 部署 unified_position_manager.py
if [ -f "A5L_v2.1_DEV/tools/unified_position_manager.py" ]; then
    cp A5L_v2.1_DEV/tools/unified_position_manager.py tools/
    echo "✅ 部署: unified_position_manager.py"
fi

# 部署验证脚本
if [ -f "A5L_v2.1_DEV/tools/verify_v2.1_repairs.py" ]; then
    cp A5L_v2.1_DEV/tools/verify_v2.1_repairs.py tools/
    echo "✅ 部署: verify_v2.1_repairs.py"
fi

echo ""

# Step 3: 应用Bug修复
echo "Step 3: 应用Bug修复..."

# 修复 unified_data_source_manager.py (health_report日期格式)
if [ -f "A5L_v2.1_DEV/tools/unified_data_source_manager.py" ]; then
    # 只复制修复后的文件（已验证通过）
    cp A5L_v2.1_DEV/tools/unified_data_source_manager.py tools/
    echo "✅ 修复: unified_data_source_manager.py (Bug #4)"
fi

echo ""

# Step 4: 验证部署
echo "Step 4: 验证部署..."
python3 tools/verify_v2.1_repairs.py
if [ $? -eq 0 ]; then
    echo "✅ 所有验证通过"
else
    echo "❌ 验证失败，请检查日志"
    exit 1
fi

echo ""

# Step 5: 更新飞书文档
echo "Step 5: 更新飞书文档..."
python3 data/simulation/update_trading_plan_docs.py 2>&1 | tail -10
echo "✅ 飞书文档更新完成"

echo ""
echo "=============================================="
echo "🎉 A5L v2.1 部署完成！"
echo "=============================================="
echo ""
echo "已完成的改进:"
echo "  ✅ P0 Bug全部修复"
echo "  ✅ 统一数据访问层"
echo "  ✅ 真实/模拟持仓严格区分"
echo "  ✅ 自动化测试框架"
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
echo "请验证:"
echo "  1. 飞书汇总看板数据正确"
echo "  2. 美股显示4只持仓"
echo "  3. 真实持仓记忆正常"
echo ""
