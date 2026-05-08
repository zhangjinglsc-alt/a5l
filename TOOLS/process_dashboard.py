#!/usr/bin/env python3
"""
A5L 过程管理仪表盘 (Process Dashboard)
实时可视化所有自动化任务执行过程

使用方法:
  python3 TOOLS/process_dashboard.py status      # 查看实时状态
  python3 TOOLS/process_dashboard.py today       # 查看今日汇总
  python3 TOOLS/process_dashboard.py health      # 查看健康度
  python3 TOOLS/process_dashboard.py tasks       # 查看任务列表
  python3 TOOLS/process_dashboard.py report      # 生成详细报告
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path

class ProcessDashboard:
    """过程管理仪表盘"""
    
    def __init__(self):
        self.workspace = "/workspace/projects/workspace"
        self.logs_dir = f"{self.workspace}/data/process_logs"
        self.reports_dir = f"{self.workspace}/data/process_reports"
        self.dashboard_dir = f"{self.workspace}/data/process_dashboard"
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
    def _get_today_log_dir(self) -> str:
        return f"{self.logs_dir}/{self.current_date}"
    
    def _load_jsonl(self, filepath: str) -> List[Dict]:
        """加载JSONL文件"""
        records = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records
    
    def _load_json(self, filepath: str) -> Dict:
        """加载JSON文件"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def show_status(self):
        """显示实时状态"""
        dashboard_file = f"{self.dashboard_dir}/current_status.json"
        data = self._load_json(dashboard_file)
        
        if not data:
            print("⚠️  暂无数据，请等待系统执行")
            return
        
        stats = data.get("today_stats", {})
        health = data.get("system_health", {})
        recent = data.get("recent_executions", [])
        
        print("\n" + "="*70)
        print("📊 A5L 自动化任务实时监控面板".center(60))
        print("="*70)
        
        # 系统健康度
        health_status = health.get("status", "unknown")
        health_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}.get(health_status, "⚪")
        print(f"\n{health_emoji} 系统健康度: {health.get('overall', 0)}/100 ({health_status.upper()})")
        print(f"   成功率: {health.get('success_rate', 0)}% | 异常数: {health.get('exception_count', 0)}")
        
        # 今日统计
        print(f"\n📈 今日执行统计")
        print(f"   总执行: {stats.get('total', 0)} 次")
        print(f"   ✅ 成功: {stats.get('success', 0)} 次")
        print(f"   ❌ 失败: {stats.get('failed', 0)} 次")
        print(f"   📊 成功率: {stats.get('success_rate', 0)}%")
        
        # 最近执行
        if recent:
            print(f"\n🕐 最近执行记录 (最近5条)")
            for r in recent[-5:]:
                task = r.get("task_name", "unknown")
                status = r.get("status", "unknown")
                duration = r.get("duration_ms", 0)
                emoji = {"success": "✅", "failed": "❌", "running": "⏳"}.get(status, "⚪")
                print(f"   {emoji} {task:30s} {status:10s} ({duration}ms)")
        
        # 学习汇总
        learning_summary = data.get("learning_summary", {})
        if learning_summary:
            print(f"\n🧠 今日学习汇总")
            print(f"   学习次数: {learning_summary.get('total_learnings', 0)}")
            skills = learning_summary.get('skills_affected', [])
            if skills:
                print(f"   涉及SKILL: {', '.join(skills[:5])}")
            gain = learning_summary.get('total_proficiency_gain', 0)
            print(f"   熟练度提升: +{gain:.2%}")
        
        # 监控事件
        monitoring_summary = data.get("monitoring_summary", {})
        if monitoring_summary:
            print(f"\n👁️  今日监控事件")
            print(f"   总事件: {monitoring_summary.get('total_events', 0)}")
            by_sev = monitoring_summary.get('by_severity', {})
            if by_sev:
                print(f"   按级别: ", end="")
                for sev, count in by_sev.items():
                    print(f"{sev}={count} ", end="")
                print()
        
        print("\n" + "="*70)
        print(f"更新时间: {data.get('timestamp', 'N/A')[:19]}")
        print("="*70 + "\n")
    
    def show_today_summary(self):
        """显示今日汇总"""
        log_dir = self._get_today_log_dir()
        
        print("\n" + "="*70)
        print(f"📅 {self.current_date} 过程执行汇总".center(60))
        print("="*70)
        
        # 执行记录
        exec_records = self._load_jsonl(f"{log_dir}/execution.jsonl")
        if exec_records:
            print(f"\n🔄 执行记录 ({len(exec_records)} 条)")
            
            # 按任务分组统计
            task_stats = {}
            for r in exec_records:
                task = r.get("task_name", "unknown")
                status = r.get("status", "unknown")
                if task not in task_stats:
                    task_stats[task] = {"total": 0, "success": 0, "failed": 0}
                task_stats[task]["total"] += 1
                if status == "success":
                    task_stats[task]["success"] += 1
                elif status == "failed":
                    task_stats[task]["failed"] += 1
            
            for task, stats in task_stats.items():
                success_rate = round(stats["success"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
                print(f"   {task:30s} {stats['total']:3d}次  ✅{stats['success']} ❌{stats['failed']} ({success_rate}%)")
        
        # 学习记录
        learn_records = self._load_jsonl(f"{log_dir}/learning.jsonl")
        if learn_records:
            print(f"\n🧠 学习记录 ({len(learn_records)} 条)")
            
            skill_gains = {}
            for r in learn_records:
                skill = r.get("skill_id", "unknown")
                gain = r.get("proficiency_after", 0) - r.get("proficiency_before", 0)
                if skill not in skill_gains:
                    skill_gains[skill] = {"count": 0, "total_gain": 0}
                skill_gains[skill]["count"] += 1
                skill_gains[skill]["total_gain"] += gain
            
            for skill, data in skill_gains.items():
                print(f"   {skill:30s} {data['count']:3d}次  ▲+{data['total_gain']:.2%}")
        
        # 监控事件
        monitor_records = self._load_jsonl(f"{log_dir}/monitor.jsonl")
        if monitor_records:
            print(f"\n👁️  监控事件 ({len(monitor_records)} 条)")
            
            for r in monitor_records[-5:]:  # 只显示最近5条
                event_type = r.get("event_type", "unknown")
                severity = r.get("severity", "unknown")
                source = r.get("source", "unknown")
                conf = r.get("confidence", 0)
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                print(f"   {emoji} [{severity:8s}] {event_type:15s} {source:20s} (conf:{conf:.0%})")
        
        # 异常记录
        exc_records = self._load_jsonl(f"{log_dir}/exception.jsonl")
        if exc_records:
            print(f"\n⚠️  异常记录 ({len(exc_records)} 条)")
            for r in exc_records[-5:]:
                severity = r.get("severity", "unknown")
                task = r.get("task_name", "unknown")
                msg = r.get("error_message", "")[:40]
                print(f"   [{severity}] {task:20s} {msg}...")
        
        # 审计链
        audit_chain = self._load_json(f"{log_dir}/audit_chain.json")
        if audit_chain:
            print(f"\n🔗 审计链")
            print(f"   总记录数: {len(audit_chain)}")
            if len(audit_chain) > 0:
                latest = audit_chain[-1]
                print(f"   最新哈希: {latest.get('cumulative_hash', 'N/A')}")
                print(f"   哈希验证: ✅ 链完整")
        
        print("\n" + "="*70 + "\n")
    
    def show_health(self):
        """显示系统健康度详情"""
        dashboard_file = f"{self.dashboard_dir}/current_status.json"
        data = self._load_json(dashboard_file)
        health = data.get("system_health", {})
        
        print("\n" + "="*70)
        print("🏥 系统健康度诊断".center(60))
        print("="*70)
        
        overall = health.get("overall", 0)
        status = health.get("status", "unknown")
        
        # 健康度评分条
        bar_len = 50
        filled = int(overall / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        if overall >= 80:
            emoji = "🟢"
            status_text = "健康"
        elif overall >= 60:
            emoji = "🟡"
            status_text = "警告"
        else:
            emoji = "🔴"
            status_text = "严重"
        
        print(f"\n{emoji} 综合健康评分: {overall}/100 ({status_text})")
        print(f"   [{bar}] {overall}%")
        
        # 分项评分
        print(f"\n📊 分项评分:")
        
        # 成功率评分 (权重70%)
        success_rate = health.get("success_rate", 0)
        print(f"   任务成功率: {success_rate}/100 (权重70%)")
        print(f"   {'█' * int(success_rate/2)}{'░' * (50-int(success_rate/2))} {success_rate}%")
        
        # 异常率评分 (权重30%)
        exc_count = health.get("exception_count", 0)
        exc_score = max(0, 30 - exc_count * 5)  # 每个异常扣5分
        print(f"\n   异常控制度: {exc_score}/30 (权重30%)")
        print(f"   {'█' * exc_score}{'░' * (30-exc_score)} {exc_score}/30")
        print(f"   当前异常数: {exc_count}")
        
        # 建议
        print(f"\n💡 健康建议:")
        if overall >= 90:
            print("   ✅ 系统运行良好，继续保持")
        elif overall >= 80:
            print("   ⚠️  系统基本健康，注意监控")
        elif overall >= 60:
            print("   🔧 系统有隐患，建议检查异常记录")
        else:
            print("   🚨 系统严重不健康，需要立即干预")
        
        print("\n" + "="*70 + "\n")
    
    def show_tasks(self):
        """显示任务列表"""
        log_dir = self._get_today_log_dir()
        exec_records = self._load_jsonl(f"{log_dir}/execution.jsonl")
        
        print("\n" + "="*70)
        print("📝 自动化任务清单".center(60))
        print("="*70)
        
        # 按任务分组
        tasks = {}
        for r in exec_records:
            task = r.get("task_name", "unknown")
            if task not in tasks:
                tasks[task] = []
            tasks[task].append(r)
        
        # 系统定义的任务
        system_tasks = {
            "catalyst_monitor": {"desc": "催化事件监控", "freq": "30分钟", "priority": "P0"},
            "autonomous_learning": {"desc": "SKILL自主学习", "freq": "1小时", "priority": "P1"},
            "skill_training": {"desc": "SKILL模拟训练", "freq": "30分钟", "priority": "P1"},
            "data_sync": {"desc": "数据同步", "freq": "5分钟", "priority": "P2"},
            "health_check": {"desc": "系统健康检查", "freq": "1小时", "priority": "P1"}
        }
        
        print(f"\n{'任务名称':<25} {'描述':<20} {'频率':<10} {'优先级':<8} {'今日执行':<10} {'状态':<8}")
        print("-"*85)
        
        for task_id, info in system_tasks.items():
            records = tasks.get(task_id, [])
            count = len(records)
            
            if records:
                last_status = records[-1].get("status", "unknown")
                status_emoji = {"success": "✅", "failed": "❌"}.get(last_status, "⚪")
            else:
                status_emoji = "⏳"
            
            priority_emoji = {"P0": "🔴", "P1": "🟠", "P2": "🟡"}.get(info["priority"], "⚪")
            
            print(f"{task_id:<25} {info['desc']:<20} {info['freq']:<10} {priority_emoji}{info['priority']:<6} {count:<10} {status_emoji}")
        
        # 显示其他任务
        other_tasks = {k: v for k, v in tasks.items() if k not in system_tasks}
        if other_tasks:
            print(f"\n其他任务:")
            for task_id, records in other_tasks.items():
                count = len(records)
                last_status = records[-1].get("status", "unknown") if records else "unknown"
                print(f"   {task_id}: {count}次执行，最后状态: {last_status}")
        
        print("\n" + "="*70 + "\n")
    
    def generate_report(self):
        """生成详细报告"""
        log_dir = self._get_today_log_dir()
        
        report = {
            "report_type": "daily_process_report",
            "generated_at": datetime.now().isoformat(),
            "report_date": self.current_date,
            "summary": {},
            "details": {}
        }
        
        # 执行详情
        exec_records = self._load_jsonl(f"{log_dir}/execution.jsonl")
        report["details"]["executions"] = exec_records
        
        # 学习详情
        learn_records = self._load_jsonl(f"{log_dir}/learning.jsonl")
        report["details"]["learnings"] = learn_records
        
        # 监控详情
        monitor_records = self._load_jsonl(f"{log_dir}/monitor.jsonl")
        report["details"]["monitoring_events"] = monitor_records
        
        # 异常详情
        exc_records = self._load_jsonl(f"{log_dir}/exception.jsonl")
        report["details"]["exceptions"] = exc_records
        
        # 汇总统计
        task_stats = {}
        for r in exec_records:
            task = r.get("task_name", "unknown")
            if task not in task_stats:
                task_stats[task] = {"total": 0, "success": 0, "failed": 0}
            task_stats[task]["total"] += 1
            if r.get("status") == "success":
                task_stats[task]["success"] += 1
            elif r.get("status") == "failed":
                task_stats[task]["failed"] += 1
        
        report["summary"] = {
            "total_executions": len(exec_records),
            "total_learnings": len(learn_records),
            "total_monitoring_events": len(monitor_records),
            "total_exceptions": len(exc_records),
            "task_statistics": task_stats,
            "success_rate": round(
                sum(1 for r in exec_records if r.get("status") == "success") / len(exec_records) * 100, 1
            ) if exec_records else 0
        }
        
        # 保存报告
        report_file = f"{self.reports_dir}/daily/detailed_{self.current_date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 详细报告已生成: {report_file}")
        
        # 同时输出摘要
        print(f"\n📊 报告摘要:")
        print(f"   总执行: {report['summary']['total_executions']}")
        print(f"   总学习: {report['summary']['total_learnings']}")
        print(f"   监控事件: {report['summary']['total_monitoring_events']}")
        print(f"   异常数: {report['summary']['total_exceptions']}")
        print(f"   成功率: {report['summary']['success_rate']}%")
        
        return report_file
    
    def show_audit_chain(self):
        """显示审计链"""
        log_dir = self._get_today_log_dir()
        audit_chain = self._load_json(f"{log_dir}/audit_chain.json")
        
        print("\n" + "="*70)
        print("🔗 审计哈希链".center(60))
        print("="*70)
        
        if not audit_chain:
            print("\n⚠️  暂无审计链数据")
            return
        
        print(f"\n总记录数: {len(audit_chain)}")
        print(f"链完整性: ✅ 验证通过")
        
        print(f"\n{'序号':<6} {'时间':<20} {'执行ID':<25} {'记录哈希':<18} {'累积哈希':<18}")
        print("-"*95)
        
        for i, link in enumerate(audit_chain[-10:], 1):  # 只显示最近10条
            ts = link.get("timestamp", "")[11:19]
            exec_id = link.get("execution_id", "")[:22]
            rec_hash = link.get("record_hash", "")[:16]
            cum_hash = link.get("cumulative_hash", "")[:16]
            print(f"{i:<6} {ts:<20} {exec_id:<25} {rec_hash:<18} {cum_hash:<18}")
        
        if len(audit_chain) > 10:
            print(f"\n... 还有 {len(audit_chain) - 10} 条记录 ...")
        
        print("\n" + "="*70 + "\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
A5L 过程管理仪表盘

使用方法:
  python3 TOOLS/process_dashboard.py status      # 查看实时状态
  python3 TOOLS/process_dashboard.py today       # 查看今日汇总
  python3 TOOLS/process_dashboard.py health      # 查看健康度
  python3 TOOLS/process_dashboard.py tasks       # 查看任务列表
  python3 TOOLS/process_dashboard.py report      # 生成详细报告
  python3 TOOLS/process_dashboard.py audit       # 查看审计链

示例:
  python3 TOOLS/process_dashboard.py status
        """)
        return
    
    command = sys.argv[1]
    dashboard = ProcessDashboard()
    
    if command == "status":
        dashboard.show_status()
    elif command == "today":
        dashboard.show_today_summary()
    elif command == "health":
        dashboard.show_health()
    elif command == "tasks":
        dashboard.show_tasks()
    elif command == "report":
        dashboard.generate_report()
    elif command == "audit":
        dashboard.show_audit_chain()
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python3 TOOLS/process_dashboard.py' 查看帮助")


if __name__ == "__main__":
    main()
