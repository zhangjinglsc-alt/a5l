#!/bin/bash
# A5L P0 Skills 一键安装脚本
# Phase 1: 安装 - 确保所有技能可用

set -e  # 遇到错误立即退出

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 A5L P0 Skills Installation Script                     ║"
echo "║     Phase 1: Installation                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0

# 检查Python版本
echo "📋 Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "   ${GREEN}✓ Python version OK${NC}"
    ((PASSED++))
else
    echo -e "   ${RED}✗ Python 3.8+ required${NC}"
    ((FAILED++))
    exit 1
fi

# 安装依赖
echo ""
echo "📦 Step 2: Installing dependencies..."

# 核心依赖
DEPS=(
    "numpy>=1.21.0"
    "pandas>=1.3.0"
    "requests>=2.26.0"
    "scipy>=1.7.0"
    "networkx>=2.6.0"
    "schedule>=1.1.0"
    "plotly>=5.3.0"
)

for dep in "${DEPS[@]}"; do
    echo -n "   Installing $dep... "
    if pip install -q "$dep" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
done

# 测试核心SKILL导入
echo ""
echo "🧪 Step 3: Testing core SKILL imports..."

SKILLS=(
    "ARCHITECT_5L.layer3_analysis.analyzers.value_cell_analyzer:VALUECellAnalyzer"
    "ARCHITECT_5L.layer3_analysis.analyzers.bearish_perspective_analyzer:BearishPerspectiveAnalyzer"
    "ARCHITECT_5L.layer3_analysis.analyzers.industry_chain_analyzer:IndustryChainAnalyzer"
    "ARCHITECT_5L.p0_skills.layer1_data_quality_monitor:DataQualityMonitor"
    "ARCHITECT_5L.p0_skills.layer1_data_access_control:DataAccessControl"
    "ARCHITECT_5L.p0_skills.layer2_strategy_version_manager:StrategyVersionManager"
    "ARCHITECT_5L.p0_skills.layer2_macro_timing_model:MacroTimingModel"
    "ARCHITECT_5L.p0_skills.layer3_reasoning_chain:ReasoningChain"
    "ARCHITECT_5L.p0_skills.layer3_bias_detector:BiasDetector"
    "ARCHITECT_5L.p0_skills.layer4_decision_audit_log:DecisionAuditLog"
    "ARCHITECT_5L.p0_skills.layer4_risk_circuit_breaker:RiskCircuitBreaker"
    "ARCHITECT_5L.p0_skills.layer5_review_workflow:ReviewWorkflow"
    "ARCHITECT_5L.p0_skills.layer5_attribution_analysis:AttributionAnalyzer"
)

for skill in "${SKILLS[@]}"; do
    IFS=':' read -r module class <<< "$skill"
    echo -n "   Testing $class... "
    
    if python3 -c "from $module import $class; print('OK')" 2>/dev/null | grep -q "OK"; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
done

# 测试Super SKILL
echo ""
echo "🔧 Step 4: Testing Super SKILL..."
echo -n "   Testing Architect5LSuperSkill... "

if python3 -c "
import sys
sys.path.insert(0, '/workspace/projects/workspace')
from skills.ARCHITECT_5L_SUPER.SKILL import Architect5LSuperSkill
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

# 运行快速测试
echo ""
echo "⚡ Step 5: Running quick tests..."

echo -n "   Testing VALUE CELL analyzer... "
if python3 -c "
import sys
sys.path.insert(0, '/workspace/projects/workspace')
from ARCHITECT_5L.layer3_analysis.analyzers.value_cell_analyzer import VALUECellAnalyzer
analyzer = VALUECellAnalyzer()
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

echo -n "   Testing Data Quality Monitor... "
if python3 -c "
import sys
sys.path.insert(0, '/workspace/projects/workspace')
from ARCHITECT_5L.p0_skills.layer1_data_quality_monitor import DataQualityMonitor
monitor = DataQualityMonitor()
result = monitor.check_data_source_health('test')
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

# 生成安装报告
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                     📊 Installation Report"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All P0 skills installed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run 'python3 -m skills.ARCHITECT-5L-SUPER.SKILL' to test Super SKILL"
    echo "  2. See A5L_SKILL_UPGRADE_PLAN.md for Phase 2"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the errors above.${NC}"
    echo ""
    exit 1
fi
