#!/bin/bash
# A5L集成数据解析脚本
# 使用FinceptTerminal解析历史数据并导入CIO系统

echo "=============================================="
echo "🔧 A5L - FinceptTerminal 数据集成"
echo "=============================================="
echo ""

ZIP_FILE="${1:-/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price.zip}"
OUTPUT_DIR="/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/processed"

echo "📦 数据文件: $ZIP_FILE"
echo "📁 输出目录: $OUTPUT_DIR"
echo ""

# 检查文件
if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ 错误: 找不到文件 $ZIP_FILE"
    echo ""
    echo "请提供正确的zip文件路径:"
    echo "   bash integrate_fincept.sh /path/to/your/data.zip"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 运行FinceptTerminal解析
echo "🚀 启动FinceptTerminal解析..."
echo "=============================================="
python3 /workspace/projects/workspace/skills/finceptterminal/fincept_terminal.py "$ZIP_FILE" -o "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ 数据解析完成!"
    echo "=============================================="
    echo ""
    echo "下一步: 开始ML模型训练"
    echo "   python3 /workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/cio_historical_trainer.py"
    echo ""
else
    echo ""
    echo "⚠️ 解析过程可能有错误，请检查日志"
fi
