#!/usr/bin/env python3
"""
月度SKILL审计调度器
每月第一个周日自动执行
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from calendar import monthcalendar

sys.path.insert(0, '/workspace/projects/workspace')

class MonthlyAuditScheduler:
    """月度审计调度器"""
    
    def __init__(self):
        self.config_path = "/workspace/projects/workspace/config/monthly_audit_config.json"
        self.log_path = "/workspace/projects/workspace/logs/monthly_audit.log"
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置"""
        default_config = {
            'enabled': True,
            'schedule': {
                'day': 'first_sunday',  # 每月第一个周日
                'time': '09:00'
            },
            'notifications': {
                'feishu': True,
                'email': False
            },
            'auto_actions': {
                'mark_deprecated': False,  # 自动标记废弃
                'generate_report': True     # 自动生成报告
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
        except:
            pass
        
        return default_config
    
    def get_next_audit_date(self) -> datetime:
        """获取下次审计日期"""
        today = datetime.now()
        
        # 获取下月日历
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year
        
        cal = monthcalendar(next_year, next_month)
        
        # 找到第一个周日
        first_sunday = None
        for week in cal:
            if week[6] != 0:  # 周日索引为6
                first_sunday = week[6]
                break
        
        # 构建日期时间
        audit_date = datetime(
            next_year, 
            next_month, 
            first_sunday,
            9, 0, 0
        )
        
        return audit_date
    
    def generate_cron_expression(self) -> str:
        """生成CRON表达式"""
        # 每月第一个周日9:00执行
        # CRON: 0 9 1-7 * 0 (每月1-7日中周日的9:00)
        return "0 9 1-7 * 0"
    
    def setup_cron_job(self):
        """设置CRON任务"""
        print("=" * 80)
        print("📅 月度SKILL审计 - CRON设置")
        print("=" * 80)
        
        cron_expr = self.generate_cron_expression()
        command = f"cd /workspace/projects/workspace && python3 ARCHITECT_5L/layer0_control/skill_lifecycle_manager.py >> logs/monthly_audit.log 2>&1"
        
        print(f"\n🕐 执行时间: 每月第一个周日 09:00")
        print(f"📋 CRON表达式: {cron_expr}")
        print(f"🔧 执行命令: {command}")
        
        print(f"\n💡 手动设置方法:")
        print(f"   1. 执行: crontab -e")
        print(f"   2. 添加以下行:")
        print(f"      {cron_expr} {command}")
        print(f"   3. 保存退出")
        
        # 生成crontab建议
        crontab_content = f"""# A5L Monthly SKILL Audit
# 每月第一个周日 09:00 执行
{cron_expr} {command}
"""
        
        # 保存建议文件
        cron_suggestion_path = "/workspace/projects/workspace/config/cron_suggestion.txt"
        Path(cron_suggestion_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(cron_suggestion_path, 'w', encoding='utf-8') as f:
            f.write(crontab_content)
        
        print(f"\n💾 CRON建议已保存: {cron_suggestion_path}")
        
        return {
            'cron_expression': cron_expr,
            'command': command,
            'next_run': self.get_next_audit_date().strftime('%Y-%m-%d %H:%M')
        }
    
    def preview_next_audits(self, months: int = 6):
        """预览未来审计日期"""
        print("\n" + "=" * 80)
        print("📅 未来审计计划预览")
        print("=" * 80)
        
        today = datetime.now()
        
        for i in range(months):
            # 计算月份
            month_offset = today.month + i
            year = today.year + (month_offset - 1) // 12
            month = ((month_offset - 1) % 12) + 1
            
            # 获取该月第一个周日
            cal = monthcalendar(year, month)
            first_sunday = None
            for week in cal:
                if week[6] != 0:
                    first_sunday = week[6]
                    break
            
            audit_date = datetime(year, month, first_sunday, 9, 0)
            
            # 判断是否是下个月
            is_next = i == 1
            marker = " <-- 下次" if is_next else ""
            
            print(f"   {year}年{month}月: {audit_date.strftime('%Y-%m-%d')} (周日) 09:00{marker}")
    
    def run_audit_now(self):
        """立即运行审计"""
        print("\n" + "=" * 80)
        print("🚀 立即执行月度审计")
        print("=" * 80)
        
        # 导入并运行审计
        from skill_lifecycle_manager import MonthlySkillAuditor
        
        auditor = MonthlySkillAuditor()
        auditor.run_monthly_audit()
    
    def generate_setup_script(self):
        """生成设置脚本"""
        script_content = '''#!/bin/bash
# A5L 月度SKILL审计 - 自动设置脚本

echo "========================================"
echo "📅 设置A5L月度SKILL审计"
echo "========================================"

# 创建日志目录
mkdir -p /workspace/projects/workspace/logs

# 添加到crontab
crontab -l > /tmp/current_crontab 2>/dev/null || true

# 检查是否已存在
if grep -q "skill_lifecycle_manager.py" /tmp/current_crontab; then
    echo "✅ CRON任务已存在，跳过设置"
else
    echo "" >> /tmp/current_crontab
    echo "# A5L Monthly SKILL Audit - 每月第一个周日9:00" >> /tmp/current_crontab
    echo "0 9 1-7 * 0 cd /workspace/projects/workspace && python3 ARCHITECT_5L/layer0_control/skill_lifecycle_manager.py >> logs/monthly_audit.log 2>&1" >> /tmp/current_crontab
    
    crontab /tmp/current_crontab
    echo "✅ CRON任务已添加"
fi

# 显示当前crontab
echo ""
echo "📋 当前CRON任务:"
crontab -l | grep -A1 "A5L Monthly" || echo "未找到"

echo ""
echo "========================================"
echo "✅ 设置完成！"
echo "下次审计: $(date -d 'next month' +%Y年%m月)第一个周日 09:00"
echo "========================================"
'''
        
        script_path = "/workspace/projects/workspace/scripts/setup_monthly_audit.sh"
        Path(script_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 添加执行权限
        import os
        os.chmod(script_path, 0o755)
        
        print(f"\n💾 设置脚本已生成: {script_path}")
        print(f"\n🚀 执行以下命令完成设置:")
        print(f"   bash {script_path}")
        
        return script_path


if __name__ == "__main__":
    scheduler = MonthlyAuditScheduler()
    
    print("=" * 80)
    print("📅 A5L 月度SKILL审计调度器")
    print("=" * 80)
    
    # 1. 显示下次审计日期
    next_audit = scheduler.get_next_audit_date()
    print(f"\n🗓️  下次审计日期: {next_audit.strftime('%Y年%m月%d日 %H:%M')}")
    
    # 2. 设置CRON任务
    cron_info = scheduler.setup_cron_job()
    
    # 3. 预览未来审计
    scheduler.preview_next_audits(months=6)
    
    # 4. 生成设置脚本
    script_path = scheduler.generate_setup_script()
    
    print("\n" + "=" * 80)
    print("✅ 月度审计调度器配置完成!")
    print("=" * 80)
    print(f"\n📋 总结:")
    print(f"   执行时间: 每月第一个周日 09:00")
    print(f"   下次审计: {next_audit.strftime('%Y-%m-%d %H:%M')}")
    print(f"   CRON设置: bash {script_path}")
    print(f"   手动执行: python3 ARCHITECT_5L/layer0_control/skill_lifecycle_manager.py")
