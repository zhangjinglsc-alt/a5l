#!/bin/bash
# ARCHITECT-5L 仪表板启动脚本

echo "🚀 启动 ARCHITECT-5L Web仪表板..."

# 检查streamlit是否安装
if ! command -v streamlit &> /dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 选择启动版本
echo ""
echo "选择仪表板版本:"
echo "1. 基础版 (app.py)"
echo "2. 增强版 (app_v2.py) - 推荐"
echo ""

# 默认启动增强版
APP_FILE="${1:-app_v2.py}"

if [ ! -f "$APP_FILE" ]; then
    echo "⚠️ $APP_FILE 不存在，使用基础版"
    APP_FILE="app.py"
fi

# 启动仪表板
echo "🌐 启动: $APP_FILE"
echo "🌐 仪表板地址: http://localhost:8501"
echo ""
streamlit run "$APP_FILE" --server.port=8501 --server.address=0.0.0.0
