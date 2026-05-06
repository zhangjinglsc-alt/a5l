#!/bin/bash
# 研报自动归档脚本
# 用于扫描本地研报目录并同步到飞书知识库

set -e

WORKSPACE="/workspace/projects/workspace"
REPORT_DIR="$WORKSPACE/data/stock_research"
CONFIG_FILE="$REPORT_DIR/.report_archive.json"
LOG_FILE="$REPORT_DIR/.archive.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${YELLOW}[INFO]${NC} [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查配置
if [ ! -f "$CONFIG_FILE" ]; then
    log_error "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 扫描本地文件
scan_local_files() {
    log_info "开始扫描本地研报目录..."
    
    local total_files=0
    local categories=("industry" "company" "macro" "strategy")
    
    for category in "${categories[@]}"; do
        local category_path="$REPORT_DIR/$category"
        if [ -d "$category_path" ]; then
            local count=$(find "$category_path" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.doc" -o -name "*.xlsx" -o -name "*.xls" -o -name "*.md" \) | wc -l)
            log_info "$category 目录: $count 个文件"
            total_files=$((total_files + count))
        fi
    done
    
    log_info "总计: $total_files 个研报文件"
    echo "$total_files"
}

# 生成扫描报告
generate_report() {
    log_info "生成扫描报告..."
    
    local report_file="$REPORT_DIR/.scan_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "scan_time": "$(date -Iseconds)",
    "local_path": "$REPORT_DIR",
    "categories": {
        "industry": $(find "$REPORT_DIR/industry" -type f 2>/dev/null | wc -l),
        "company": $(find "$REPORT_DIR/company" -type f 2>/dev/null | wc -l),
        "macro": $(find "$REPORT_DIR/macro" -type f 2>/dev/null | wc -l),
        "strategy": $(find "$REPORT_DIR/strategy" -type f 2>/dev/null | wc -l)
    }
}
EOF

    log_success "扫描报告已保存: $report_file"
}

# 主函数
main() {
    log "=========================================="
    log "研报自动归档任务开始"
    log "=========================================="
    
    # 确保目录结构存在
    mkdir -p "$REPORT_DIR"/{industry,company,macro,strategy}
    
    # 扫描本地文件
    local total=$(scan_local_files)
    
    # 生成报告
    generate_report
    
    # 更新配置中的最后扫描时间
    local temp_config="$CONFIG_FILE.tmp"
    jq --arg time "$(date -Iseconds)" '.last_scan = $time' "$CONFIG_FILE" > "$temp_config" && mv "$temp_config" "$CONFIG_FILE"
    
    log "=========================================="
    if [ "$total" -eq 0 ]; then
        log_info "当前无新增研报需要归档"
    else
        log_success "扫描完成，共 $total 个研报文件"
        log_info "请将新研报放入对应目录后手动触发同步"
    fi
    log "=========================================="
}

# 执行主函数
main "$@"
