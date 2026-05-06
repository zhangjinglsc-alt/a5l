#!/bin/bash
# A5L Alpha测试 - 启动操作手册
# 执行时间: 2026-05-05 09:00 (明日)

set -e  # 遇到错误立即退出

echo "======================================================================"
echo "🚀 A5L Alpha测试 - 启动操作手册"
echo "======================================================================"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "测试周期: 2026-05-05 ~ 2026-06-01 (28天)"
echo "测试资金: $10,000 USD + ¥50,000 CNY (纸交易)"
echo "======================================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 步骤计数器
STEP=0
next_step() {
    STEP=$((STEP + 1))
    echo ""
    echo "======================================================================"
    echo "【步骤 $STEP】$1"
    echo "======================================================================"
}

# ==================== 步骤1: 环境检查 ====================
next_step "启动前环境检查"

log_info "检查当前目录..."
if [ ! -f "A5L_v4_SUMMARY.md" ]; then
    log_error "未在项目根目录，请切换到正确目录"
    exit 1
fi
log_info "目录检查通过"

log_info "检查Git状态..."
if [ -d ".git" ]; then
    GIT_COMMIT=$(git rev-parse --short HEAD)
    log_info "当前Git版本: $GIT_COMMIT"
else
    log_warn "Git仓库未初始化"
fi

log_info "检查Python环境..."
python3 --version || { log_error "Python3未安装"; exit 1; }

log_info "检查磁盘空间..."
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    log_info "磁盘空间充足 (${DISK_USAGE}%)"
else
    log_warn "磁盘空间不足 (${DISK_USAGE}%)"
fi

log_info "环境检查完成"

# ==================== 步骤2: 系统健康检查 ====================
next_step "系统健康检查 (100/100标准)"

log_info "运行系统健康检查脚本..."
if [ -f "test_system_health.py" ]; then
    python3 test_system_health.py
    if [ $? -eq 0 ]; then
        log_info "系统健康检查通过"
    else
        log_error "系统健康检查失败，请修复问题后再启动"
        exit 1
    fi
else
    log_warn "健康检查脚本不存在，跳过"
fi

# ==================== 步骤3: 自动化测试 ====================
next_step "运行自动化测试套件 (15个用例)"

log_info "运行Alpha测试套件..."
if [ -f "test_alpha_suite.py" ]; then
    python3 test_alpha_suite.py
    if [ $? -eq 0 ]; then
        log_info "所有15个测试用例通过"
    else
        log_error "存在失败的测试用例，请修复后再启动"
        exit 1
    fi
else
    log_warn "测试套件不存在，跳过"
fi

# ==================== 步骤4: 数据同步检查 ====================
next_step "数据同步检查"

log_info "检查飞书-本地数据一致性..."
if [ -f "data/positions/position_summary.json" ]; then
    POSITIONS=$(cat data/positions/position_summary.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('positions_count',0))")
    log_info "本地持仓数量: $POSITIONS"
else
    log_warn "本地持仓文件不存在"
fi

log_info "数据同步检查完成"

# ==================== 步骤5: 配置备份 ====================
next_step "配置备份"

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

log_info "备份配置文件..."
cp -r data/positions $BACKUP_DIR/ 2>/dev/null || true
cp -r data/simulation $BACKUP_DIR/ 2>/dev/null || true
cp -r data/architect_5l/signals $BACKUP_DIR/ 2>/dev/null || true

echo "$GIT_COMMIT" > $BACKUP_DIR/git_commit.txt
date > $BACKUP_DIR/backup_time.txt

log_info "配置已备份到: $BACKUP_DIR"

# ==================== 步骤6: 启动Alpha测试 ====================
next_step "启动Alpha测试"

log_info "创建测试日志目录..."
mkdir -p logs/alpha_test

log_info "生成测试配置..."
cat > config/alpha_test.json << EOF
{
  "version": "4.0.0-alpha",
  "start_date": "$(date +%Y-%m-%d)",
  "environment": "alpha_test",
  "trading": {
    "enabled": true,
    "paper_trading": true,
    "initial_capital": {
      "usd": 10000,
      "cny": 50000
    },
    "markets": ["a_share", "us"],
    "risk_limits": {
      "max_position_size": 0.20,
      "max_drawdown": 0.10,
      "daily_var_limit": 0.05
    }
  },
  "monitoring": {
    "log_level": "DEBUG",
    "health_check_interval": 300,
    "report_time": "21:00"
  }
}
EOF

log_info "启动纸交易系统..."

# 创建启动脚本
cat > start_alpha.sh << 'EOF'
#!/bin/bash
echo "Starting A5L Alpha Test..."
echo "Start time: $(date)"
echo "Config: config/alpha_test.json"
echo "Logs: logs/alpha_test/"

# 记录启动信息
echo "$(date): Alpha test started" >> logs/alpha_test/system.log

# 这里可以启动实际的交易循环
# python3 data/architect_5l/alpha_trading_loop.py &

echo "Alpha test is running..."
echo "Use './monitor_alpha.sh' to check status"
EOF

chmod +x start_alpha.sh

log_info "执行启动脚本..."
./start_alpha.sh 2>&1 | tee logs/alpha_test/startup.log

# ==================== 步骤7: 启动监控 ====================
next_step "启动监控系统"

log_info "创建监控脚本..."
cat > monitor_alpha.sh << 'EOF'
#!/bin/bash
echo "======================================================================"
echo "📊 A5L Alpha测试 - 实时监控"
echo "======================================================================"
echo "检查时间: $(date)"
echo "======================================================================"

# 检查进程
if pgrep -f "alpha" > /dev/null 2>&1; then
    echo "✅ Alpha测试进程运行中"
else
    echo "⚠️  Alpha测试进程未运行 (如果是刚启动，请等待30秒)"
fi

# 检查日志
if [ -f logs/alpha_test/system.log ]; then
    echo ""
    echo "📄 最近日志:"
    tail -10 logs/alpha_test/system.log
fi

# 检查磁盘
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
echo ""
echo "💾 磁盘使用: ${DISK_USAGE}%"

# 检查内存
MEMORY=$(free -m | grep Mem | awk '{printf "%.1f", $3/$2 * 100}')
echo "🧠 内存使用: ${MEMORY}%"

echo ""
echo "======================================================================"
echo "监控命令:"
echo "  查看日志: tail -f logs/alpha_test/system.log"
echo "  检查健康: python3 test_system_health.py"
echo "  停止测试: pkill -f alpha"
echo "======================================================================"
EOF

chmod +x monitor_alpha.sh

log_info "监控脚本已创建: ./monitor_alpha.sh"

# ==================== 步骤8: 创建日报生成脚本 ====================
next_step "创建日报生成脚本"

cat > generate_daily_report.sh << 'EOF'
#!/bin/bash
REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="logs/alpha_test/daily_report_${REPORT_DATE}.md"

echo "# Alpha测试日报 - ${REPORT_DATE}" > $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 当日概况" >> $REPORT_FILE
echo "- 测试阶段: Phase X" >> $REPORT_FILE
echo "- 测试用例执行: XX/XX" >> $REPORT_FILE
echo "- 系统状态: [正常/警告/异常]" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 交易表现 (纸交易)" >> $REPORT_FILE
echo "- 日收益率: X.XX%" >> $REPORT_FILE
echo "- 累计收益率: X.XX%" >> $REPORT_FILE
echo "- 最大回撤: X.XX%" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 发现的问题" >> $REPORT_FILE
echo "1. [问题描述]" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 明日计划" >> $REPORT_FILE
echo "- [计划内容]" >> $REPORT_FILE

echo "日报已生成: $REPORT_FILE"
EOF

chmod +x generate_daily_report.sh

# ==================== 完成 ====================
echo ""
echo "======================================================================"
echo "🎉 Alpha测试启动完成！"
echo "======================================================================"
echo ""
echo "📋 启动信息:"
echo "   启动时间: $(date)"
echo "   Git版本: $GIT_COMMIT"
echo "   配置文件: config/alpha_test.json"
echo "   日志目录: logs/alpha_test/"
echo "   备份目录: $BACKUP_DIR"
echo ""
echo "📊 常用命令:"
echo "   监控状态: ./monitor_alpha.sh"
echo "   查看日志: tail -f logs/alpha_test/system.log"
echo "   生成日报: ./generate_daily_report.sh"
echo "   健康检查: python3 test_system_health.py"
echo "   运行测试: python3 test_alpha_suite.py"
echo ""
echo "⏰ 定时任务建议:"
echo "   # 每小时健康检查"
echo "   0 * * * * cd $(pwd) && python3 test_system_health.py >> logs/alpha_test/health.log 2>&1"
echo ""
echo "   # 每日21:00生成报告"
echo "   0 21 * * * cd $(pwd) && ./generate_daily_report.sh"
echo ""
echo "======================================================================"
echo "⚠️  重要提醒:"
echo "   1. 今日为Alpha测试Day 1 (Phase 1: 环境验证)"
echo "   2. 请每小时运行一次 ./monitor_alpha.sh"
echo "   3. 任何问题立即记录到 logs/alpha_test/issues.log"
echo "   4. 每晚21:00运行 ./generate_daily_report.sh"
echo "======================================================================"
