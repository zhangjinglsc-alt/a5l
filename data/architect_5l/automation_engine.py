#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 自动化运维脚本
定时任务: 健康检查、备份、监控
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, '/workspace/projects/workspace/data/architect_5l')

from production_monitor import ProductionMonitor
from realtime_price_feed import RealtimePriceFeed

class AutomationEngine:
    """自动化运维引擎"""
    
    def __init__(self):
        self.data_dir = "/workspace/projects/workspace/data/architect_5l"
        self.log_dir = f"{self.data_dir}/logs"
        self.backup_dir = f"{self.data_dir}/backups"
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def health_check(self) -> Dict:
        """系统健康检查"""
        print("🔍 执行系统健康检查...")
        
        monitor = ProductionMonitor()
        health = monitor.get_system_health()
        alerts = monitor.check_alerts()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health["overall_score"],
            "status": health["overall_status"],
            "alerts_count": len(alerts),
            "alerts": alerts
        }
        
        # 保存日志
        log_file = f"{self.log_dir}/health_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            f.write(json.dumps(result) + '\n')
        
        # 如果有严重告警，发送通知
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        if critical_alerts:
            self._send_alert("CRITICAL", f"发现 {len(critical_alerts)} 个严重告警!")
        
        print(f"   ✅ 健康得分: {result['health_score']}/100")
        print(f"   ✅ 状态: {result['status']}")
        if alerts:
            print(f"   ⚠️  告警: {len(alerts)} 个")
        
        return result
    
    def backup_system(self) -> Dict:
        """系统备份"""
        print("💾 执行系统备份...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"a5l_backup_{timestamp}"
        backup_path = f"{self.backup_dir}/{backup_name}"
        
        os.makedirs(backup_path, exist_ok=True)
        
        # 备份数据库
        db_source = f"{self.data_dir}/architect_5l.db"
        db_backup = f"{backup_path}/architect_5l.db"
        
        try:
            import shutil
            shutil.copy2(db_source, db_backup)
            print(f"   ✅ 数据库备份完成")
        except Exception as e:
            print(f"   ❌ 数据库备份失败: {e}")
        
        # 备份JSON数据
        json_files = [
            "signals/tracked_signals.json",
            "decisions/decisions.json",
            "collective_decision_system.json",
            "prediction_validation_system.json"
        ]
        
        for file in json_files:
            source = f"{self.data_dir}/{file}"
            if os.path.exists(source):
                dest = f"{backup_path}/{os.path.basename(file)}"
                shutil.copy2(source, dest)
        
        print(f"   ✅ 配置文件备份完成")
        
        # 创建备份清单
        manifest = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "files": os.listdir(backup_path),
            "size": sum(os.path.getsize(f"{backup_path}/{f}") for f in os.listdir(backup_path))
        }
        
        with open(f"{backup_path}/manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"   ✅ 备份完成: {backup_path}")
        
        # 清理旧备份 (保留最近7个)
        self._cleanup_old_backups()
        
        return manifest
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        backups = sorted([
            d for d in os.listdir(self.backup_dir)
            if d.startswith("a5l_backup_") and os.path.isdir(f"{self.backup_dir}/{d}")
        ])
        
        # 保留最近7个
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                old_path = f"{self.backup_dir}/{old_backup}"
                import shutil
                shutil.rmtree(old_path)
                print(f"   🗑️  清理旧备份: {old_backup}")
    
    def update_prices(self) -> Dict:
        """更新实时价格"""
        print("📈 更新实时价格...")
        
        feed = RealtimePriceFeed()
        
        # 关注列表
        watchlist = [
            {"symbol": "NVDA", "market": "US"},
            {"symbol": "AAPL", "market": "US"},
            {"symbol": "TSLA", "market": "US"},
            {"symbol": "000066", "market": "CN"},
            {"symbol": "688981", "market": "CN"},
            {"symbol": "00700", "market": "HK"}
        ]
        
        results = feed.batch_update(watchlist)
        
        print(f"   ✅ 更新成功: {results['success']} 个")
        print(f"   ✅ 更新失败: {results['failed']} 个")
        
        return results
    
    def validate_pending_signals(self) -> Dict:
        """验证待验证的信号"""
        print("🔄 验证待验证信号...")
        
        from prediction_validation_engine import PredictionValidationEngine
        
        engine = PredictionValidationEngine()
        pending = engine.get_pending_validations()
        
        validated = []
        for p in pending:
            # 这里会获取实际价格并验证
            # 模拟验证
            validated.append({
                "signal_id": p['signal_id'],
                "status": "pending_validation"
            })
        
        print(f"   ⏳ 待验证信号: {len(pending)} 个")
        
        return {"pending": len(pending), "validated": len(validated)}
    
    def generate_daily_report(self) -> str:
        """生成日报"""
        print("📊 生成日报...")
        
        monitor = ProductionMonitor()
        summary = monitor.get_daily_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              A5L Protocol v2.0 - 每日运营报告                  ║
╠══════════════════════════════════════════════════════════════╣
║ 日期: {summary['date']}                                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📈 信号统计                                                 ║
║  ─────────────────────────────────────────────────────────  ║
║     生成信号: {summary['signals_generated']:3d}                                 ║
║     验证信号: {summary['signals_validated']:3d}                                 ║
║                                                              ║
║  🗳️ 决策统计                                                 ║
║  ─────────────────────────────────────────────────────────  ║
║     做出决策: {summary['decisions_made']:3d}                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        # 保存报告
        report_file = f"{self.log_dir}/daily_report_{summary['date']}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"   ✅ 日报已保存: {report_file}")
        
        return report
    
    def _send_alert(self, level: str, message: str):
        """发送告警 (模拟)"""
        print(f"   🚨 [{level}] {message}")
        # 实际部署中会发送到飞书/邮件等
    
    def run_all(self):
        """运行所有任务"""
        print("=" * 70)
        print("⚙️  A5L 自动化运维任务")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 任务1: 健康检查
        print("\n[1/5] 系统健康检查")
        self.health_check()
        
        # 任务2: 更新价格
        print("\n[2/5] 更新实时价格")
        self.update_prices()
        
        # 任务3: 验证信号
        print("\n[3/5] 验证待处理信号")
        self.validate_pending_signals()
        
        # 任务4: 系统备份
        print("\n[4/5] 系统备份")
        self.backup_system()
        
        # 任务5: 生成日报
        print("\n[5/5] 生成日报")
        self.generate_daily_report()
        
        print("\n" + "=" * 70)
        print("✅ 所有任务执行完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


def main():
    """主函数"""
    engine = AutomationEngine()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        task = sys.argv[1]
        
        if task == "health":
            engine.health_check()
        elif task == "backup":
            engine.backup_system()
        elif task == "prices":
            engine.update_prices()
        elif task == "validate":
            engine.validate_pending_signals()
        elif task == "report":
            engine.generate_daily_report()
        elif task == "all":
            engine.run_all()
        else:
            print(f"未知任务: {task}")
            print("可用任务: health, backup, prices, validate, report, all")
    else:
        # 默认运行所有任务
        engine.run_all()


if __name__ == "__main__":
    main()
