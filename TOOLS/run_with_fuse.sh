#!/bin/bash
# 任务执行包装脚本，自动集成熔断机制
# 用法: run_with_fuse.sh <任务标识名> <实际执行命令>

if [ $# -lt 2 ]; then
    echo "用法: run_with_fuse.sh <任务标识名> <实际执行命令>"
    exit 1
fi

TASK_NAME="$1"
shift
CMD="$*"

CB_SCRIPT="/workspace/projects/workspace/TOOLS/task_circuit_breaker.py"

# 检查是否被熔断
python3 "$CB_SCRIPT" check "$TASK_NAME"
if [ $? -eq 1 ]; then
    echo "任务 $TASK_NAME 处于熔断状态，跳过执行"
    exit 0
fi

# 执行命令
echo "执行任务: $TASK_NAME, 命令: $CMD"
start_time=$(date +%s)
$CMD
EXIT_CODE=$?
end_time=$(date +%s)
duration=$((end_time - start_time))

# 记录执行结果
if [ $EXIT_CODE -eq 0 ]; then
    python3 "$CB_SCRIPT" record_success "$TASK_NAME"
else
    python3 "$CB_SCRIPT" record_failure "$TASK_NAME" "命令执行失败，退出码: $EXIT_CODE, 耗时: ${duration}s"
fi

exit $EXIT_CODE