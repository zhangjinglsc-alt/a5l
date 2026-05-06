#!/bin/bash
# A5L系统文件自动备份脚本
# 由Knowledge Guardian调用
# 每日执行：备份SOUL/GOAL/MEMORY等关键文件

echo "=========================================="
echo "📚 A5L Knowledge Guardian - Daily Backup"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

cd /workspace/projects/workspace

# 运行Python备份脚本
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/workspace/projects/workspace')

from ARCHITECT_5L.layer0_control.knowledge_quick_access import backup_all_system_files
from datetime import datetime

print(f"\n📅 Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("-" * 50)

# 执行备份
backed_up = backup_all_system_files()

print(f"\n✅ Backup Summary:")
print(f"   Files backed up: {len(backed_up)}")
for f in backed_up:
    filename = f.split('/')[-1]
    print(f"   • {filename}")

print("\n💾 Backup completed successfully!")
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "✅ Daily backup finished"
echo "=========================================="
