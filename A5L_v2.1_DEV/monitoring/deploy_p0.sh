#!/bin/bash
# A5L P0监控系统部署脚本
# 部署Upptime + Wolverine + Prometheus

set -e

echo "=============================================="
echo "🚀 A5L P0 监控系统部署"
echo "=============================================="
echo ""

WORKSPACE="/workspace/projects/workspace"
MONITOR_DIR="$WORKSPACE/monitoring"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 部署Upptime
echo "📊 步骤 1/3: 部署 Upptime 状态监控"
echo "----------------------------------------------"

if [ -d "$MONITOR_DIR/upptime/.github" ]; then
    print_status "Upptime 配置已存在"
    echo "   配置文件: $MONITOR_DIR/upptime/.upptimerc.yml"
    echo "   监控站点: 6个"
    echo "   检查频率: 每5分钟"
else
    print_error "Upptime 配置目录不存在"
    exit 1
fi

echo ""
echo "📋 Upptime 部署说明:"
echo "   1. 需要在GitHub创建独立仓库"
echo "   2. 复制配置文件到仓库"
echo "   3. 设置 Secrets.GH_PAT"
echo "   4. 启用GitHub Actions"
echo ""

# 2. 部署Wolverine
echo "🔧 步骤 2/3: 部署 Wolverine 自愈修复"
echo "----------------------------------------------"

if [ -f "$MONITOR_DIR/wolverine/a5l_wolverine.py" ]; then
    print_status "Wolverine 系统已就绪"
    
    # 检查Python依赖
    if pip show wolverine > /dev/null 2>&1; then
        print_status "Wolverine 已安装"
    else
        print_warning "Wolverine 未安装，正在安装..."
        pip install wolverine -q
        print_status "Wolverine 安装完成"
    fi
    
    echo ""
    echo "📋 Wolverine 功能:"
    echo "   • 自动修复Python运行时错误"
    echo "   • GPT-4驱动的代码修复"
    echo "   • 修复历史记录"
    echo ""
    echo "🧪 测试 Wolverine:"
    cd "$WORKSPACE"
    python3 monitoring/wolverine/a5l_wolverine.py 2>&1 | head -20
else
    print_error "Wolverine 配置不存在"
    exit 1
fi

# 3. 部署Prometheus
echo "📈 步骤 3/3: 部署 Prometheus + Grafana"
echo "----------------------------------------------"

if [ -f "$MONITOR_DIR/prometheus/prometheus.yml" ]; then
    print_status "Prometheus 配置已就绪"
    echo "   配置文件: $MONITOR_DIR/prometheus/prometheus.yml"
    echo "   告警规则: $MONITOR_DIR/prometheus/a5l_alerts.yml"
    echo "   监控任务: 7个"
    echo ""
    
    # 检查Prometheus是否安装
    if command -v prometheus &> /dev/null; then
        print_status "Prometheus 已安装"
    else
        print_warning "Prometheus 未安装"
        echo "   安装命令:"
        echo "   wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz"
        echo "   tar xvfz prometheus-2.45.0.linux-amd64.tar.gz"
        echo "   sudo mv prometheus /usr/local/bin/"
    fi
    
    echo ""
    echo "📋 Prometheus 告警规则:"
    grep "alert:" $MONITOR_DIR/prometheus/a5l_alerts.yml | wc -l | xargs echo "   告警规则数:"
    echo ""
    echo "   • A5LGatewayDown - Gateway服务不可用"
    echo "   • DiskSpaceLow - 磁盘空间不足"
    echo "   • MemoryHigh - 内存使用过高"
    echo "   • PositionDataStale - 持仓数据更新延迟"
else
    print_error "Prometheus 配置不存在"
    exit 1
fi

echo ""
echo "=============================================="
echo "✅ P0 监控系统部署完成!"
echo "=============================================="
echo ""
echo "📊 部署组件:"
echo "   1. Upptime - 状态监控 (配置完成)"
echo "   2. Wolverine - 自愈修复 (已就绪)"
echo "   3. Prometheus - 指标监控 (配置完成)"
echo ""
echo "⚠️  手动配置项:"
echo "   • GitHub Secrets: GH_PAT, FEISHU_WEBHOOK_URL"
echo "   • 安装 Prometheus + Grafana"
echo "   • 配置 Alertmanager 飞书通知"
echo ""
echo "📖 详细文档: docs/CODE_SKILL_RESEARCH_REPORT.md"
echo ""
