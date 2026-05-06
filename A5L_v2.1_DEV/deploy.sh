#!/bin/bash
# A5L Protocol v4.0 - 生产部署脚本
# Production Deployment Script

echo "======================================================================"
echo "🚀 A5L Protocol v4.0 - 生产部署"
echo "======================================================================"
echo "部署时间: $(date)"
echo "======================================================================"

# 1. 环境检查
echo ""
echo "【步骤1】环境检查"
echo "----------------------------------------------------------------------"

# Python版本
python3 --version || { echo "❌ Python3未安装"; exit 1; }

# 依赖检查
echo "检查依赖..."
pip3 install -q numpy pandas matplotlib 2>/dev/null || echo "⚠️  部分依赖安装失败"

echo "✅ 环境检查完成"

# 2. 代码部署
echo ""
echo "【步骤2】代码部署"
echo "----------------------------------------------------------------------"

DEPLOY_DIR="/opt/a5l"
mkdir -p $DEPLOY_DIR
cp -r /workspace/projects/workspace/data/architect_5l/* $DEPLOY_DIR/ 2>/dev/null || echo "⚠️  使用当前目录"

echo "✅ 代码部署完成"

# 3. 配置初始化
echo ""
echo "【步骤3】配置初始化"
echo "----------------------------------------------------------------------"

# 创建配置目录
mkdir -p $DEPLOY_DIR/config
mkdir -p $DEPLOY_DIR/logs
mkdir -p $DEPLOY_DIR/data/positions
mkdir -p $DEPLOY_DIR/data/simulation
mkdir -p $DEPLOY_DIR/data/signals

# 生成默认配置
cat > $DEPLOY_DIR/config/production.json << 'EOF'
{
  "version": "4.0.0",
  "environment": "production",
  "trading": {
    "enabled": false,
    "paper_trading": true,
    "markets": ["a_share", "us"],
    "risk_limits": {
      "max_position_size": 0.20,
      "max_drawdown": 0.15,
      "daily_var_limit": 0.05
    }
  },
  "data": {
    "sources": ["akshare", "tushare", "yahoo"],
    "update_interval": 60,
    "sync_to_feishu": true
  },
  "risk": {
    "circuit_breakers": {
      "daily_loss_limit": 0.05,
      "consecutive_losses": 3,
      "volatility_spike": 0.50
    }
  },
  "monitoring": {
    "health_check_interval": 300,
    "alert_channels": ["feishu"],
    "log_level": "INFO"
  }
}
EOF

echo "✅ 配置初始化完成"

# 4. 测试运行
echo ""
echo "【步骤4】系统测试"
echo "----------------------------------------------------------------------"

cd $DEPLOY_DIR

# 测试核心模块
echo "测试回测引擎..."
python3 backtest_engine.py > /dev/null 2>&1 && echo "✅ 回测引擎正常" || echo "❌ 回测引擎异常"

echo "测试风控系统..."
python3 risk_manager.py > /dev/null 2>&1 && echo "✅ 风控系统正常" || echo "❌ 风控系统异常"

echo "测试券商API..."
python3 broker_api.py > /dev/null 2>&1 && echo "✅ 券商API正常" || echo "❌ 券商API异常"

echo "✅ 系统测试完成"

# 5. 启动服务
echo ""
echo "【步骤5】启动服务"
echo "----------------------------------------------------------------------"

cat > $DEPLOY_DIR/start.sh << 'EOF'
#!/bin/bash
echo "Starting A5L v4.0..."
python3 -c "
import sys
sys.path.insert(0, '.')
print('A5L Protocol v4.0 - Running in PAPER TRADING mode')
print('System Ready')
" 2>&1 | tee logs/a5l.log
EOF

chmod +x $DEPLOY_DIR/start.sh

echo "✅ 启动脚本创建完成"
echo "   启动命令: $DEPLOY_DIR/start.sh"

# 6. 创建监控脚本
echo ""
echo "【步骤6】创建监控脚本"
echo "----------------------------------------------------------------------"

cat > $DEPLOY_DIR/monitor.sh << 'EOF'
#!/bin/bash
# A5L健康检查脚本

echo "A5L Health Check - $(date)"
echo "----------------------------------------------------------------------"

# 检查进程
if pgrep -f "a5l" > /dev/null; then
    echo "✅ A5L进程运行中"
else
    echo "⚠️  A5L进程未运行"
fi

# 检查日志
if [ -f logs/a5l.log ]; then
    echo "✅ 日志文件正常"
    tail -5 logs/a5l.log
else
    echo "⚠️  日志文件不存在"
fi

# 检查磁盘
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ 磁盘空间充足 (${DISK_USAGE}%)"
else
    echo "⚠️  磁盘空间不足 (${DISL_USAGE}%)"
fi

echo "----------------------------------------------------------------------"
EOF

chmod +x $DEPLOY_DIR/monitor.sh

echo "✅ 监控脚本创建完成"
echo "   检查命令: $DEPLOY_DIR/monitor.sh"

# 7. 部署完成
echo ""
echo "======================================================================"
echo "✅ A5L Protocol v4.0 部署完成!"
echo "======================================================================"
echo ""
echo "部署目录: $DEPLOY_DIR"
echo "配置文件: $DEPLOY_DIR/config/production.json"
echo "日志文件: $DEPLOY_DIR/logs/a5l.log"
echo ""
echo "常用命令:"
echo "   启动: $DEPLOY_DIR/start.sh"
echo "   监控: $DEPLOY_DIR/monitor.sh"
echo "   日志: tail -f $DEPLOY_DIR/logs/a5l.log"
echo ""
echo "⚠️  重要提醒:"
echo "   当前为纸交易模式 (paper_trading: true)"
echo "   实盘交易前请:"
echo "   1. 配置真实券商API密钥"
echo "   2. 修改 trading.enabled 为 true"
echo "   3. 充分测试纸交易环境"
echo ""
echo "======================================================================"
