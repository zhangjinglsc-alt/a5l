#!/usr/bin/env python3
"""
Catalyst Monitor Auto - 自动催化事件监控系统
主监控脚本
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# 添加项目根目录到路径
sys.path.insert(0, '/workspace/projects/workspace')

class CatalystMonitor:
    """催化事件监控器"""
    
    def __init__(self):
        self.base_path = Path('/workspace/projects/workspace/skills/catalyst-monitor-auto')
        self.data_path = self.base_path / 'data'
        self.events_path = self.data_path / 'events'
        self.logs_path = self.data_path / 'logs'
        
        # 确保目录存在
        self.events_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_file = self.base_path / 'references' / 'monitored_topics.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "topics": ["AI算力", "服务器CPU", "存储芯片", "光模块"],
            "stocks": ["000066", "601975", "688981"],
            "min_tier": 2
        }
    
    def start(self, topic=None, stocks=None):
        """启动监控"""
        print("🚀 启动催化事件自动监控...")
        print(f"📡 监控主题: {topic or ', '.join(self.config['topics'])}")
        print(f"📈 监控股票: {stocks or ', '.join(self.config['stocks'])}")
        print("\n💡 提示: 监控将在后台运行，通过cron定时触发")
        print("💡 使用 'monitor.py status' 查看状态")
        
        # 记录启动日志
        self._log("监控服务启动")
        
        # 立即执行一次扫描
        self.scan()
    
    def scan(self):
        """执行一次完整扫描"""
        print("🔍 执行完整扫描...")
        
        # 1. 新闻聚合搜索
        self._search_news()
        
        # 2. 分析事件
        self._analyze_events()
        
        print("✅ 扫描完成")
    
    def _search_news(self):
        """搜索新闻"""
        print("  📰 搜索新闻聚合...")
        
        # 模拟新闻搜索结果
        # 实际实现将调用统一新闻聚合skill
        topics = self.config['topics']
        
        for topic in topics:
            print(f"    - 搜索: {topic}")
            # 这里将调用实际的新闻搜索API
            # results = unified_news_search(topic)
    
    def _analyze_events(self):
        """分析事件"""
        print("  🧠 分析催化事件...")
        
        # 调用CTF分析器
        analyzer_script = self.base_path / 'scripts' / 'analyzer.py'
        if analyzer_script.exists():
            try:
                result = subprocess.run(
                    ['python3', str(analyzer_script)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"    ⚠️ 分析器错误: {result.stderr}")
            except Exception as e:
                print(f"    ⚠️ 分析失败: {e}")
    
    def analyze(self, topic):
        """分析特定主题"""
        print(f"🎯 深度分析主题: {topic}")
        
        # 1. 深度搜索
        print(f"  🔍 深度搜索: {topic}")
        # 调用coze或tavily搜索
        
        # 2. CTF分析
        print(f"  🧠 CTF分级分析...")
        # 生成分析报告
        
        # 3. 推送结果
        print(f"  📤 推送分析结果...")
        self._notify(f"主题分析: {topic}", "分析完成")
    
    def daily_report(self):
        """生成日报"""
        print("📊 生成催化事件日报...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 收集今日事件
        events = self._get_today_events()
        
        # 按Tier分级
        tier_counts = {'1': 0, '2': 0, '3': 0, '4': 0}
        for event in events:
            tier = str(event.get('tier', 4))
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        report = f"""
📊 催化事件日报 ({today})

今日识别事件: {len(events)} 个
├─ Tier 1 (范式级): {tier_counts['1']} 个
├─ Tier 2 (周期确认): {tier_counts['2']} 个
├─ Tier 3 (资金驱动): {tier_counts['3']} 个
└─ Tier 4 (补涨扩散): {tier_counts['4']} 个

重点事件:
"""
        
        for event in events[:5]:  # 前5个重要事件
            report += f"\n• [{event.get('tier', '?')}] {event.get('title', '未知')}"
        
        print(report)
        
        # 保存日报
        report_file = self.events_path / f'daily_report_{today}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 推送日报
        self._notify("催化事件日报", report)
    
    def status(self):
        """查看监控状态"""
        print("📊 监控状态")
        print(f"  配置主题: {', '.join(self.config['topics'])}")
        print(f"  监控股票: {', '.join(self.config['stocks'])}")
        print(f"  最低级别: Tier {self.config['min_tier']}")
        
        # 今日事件统计
        events = self._get_today_events()
        print(f"\n  今日事件: {len(events)} 个")
        
        if events:
            tier_dist = {}
            for e in events:
                t = e.get('tier', 4)
                tier_dist[t] = tier_dist.get(t, 0) + 1
            print(f"    Tier分布: {tier_dist}")
    
    def events(self, today=False, tier=None):
        """查看事件列表"""
        if today:
            events = self._get_today_events()
        else:
            events = self._get_all_events()
        
        if tier:
            events = [e for e in events if e.get('tier') == int(tier)]
        
        print(f"\n📋 事件列表 ({len(events)} 个)")
        print("-" * 60)
        
        for event in events[-20:]:  # 最近20个
            tier = event.get('tier', '?')
            title = event.get('title', '未知')[:40]
            time = event.get('time', '未知')
            print(f"[T{tier}] {title} ({time})")
    
    def _get_today_events(self):
        """获取今日事件"""
        today = datetime.now().strftime('%Y-%m-%d')
        events_file = self.events_path / f'events_{today}.json'
        
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _get_all_events(self):
        """获取所有事件"""
        events = []
        for f in self.events_path.glob('events_*.json'):
            with open(f, 'r', encoding='utf-8') as file:
                events.extend(json.load(file))
        return events
    
    def _notify(self, title, content):
        """推送通知"""
        notifier_script = self.base_path / 'scripts' / 'notifier.py'
        if notifier_script.exists():
            try:
                subprocess.run(
                    ['python3', str(notifier_script), title, content],
                    timeout=30
                )
            except Exception as e:
                print(f"  ⚠️ 推送失败: {e}")
    
    def _log(self, message):
        """记录日志"""
        log_file = self.logs_path / f'monitor_{datetime.now().strftime("%Y%m%d")}.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} - {message}\n")


def main():
    parser = argparse.ArgumentParser(description='自动催化事件监控系统')
    parser.add_argument('command', choices=[
        'start', 'scan', 'analyze', 'daily-report', 'status', 'events'
    ], help='命令')
    parser.add_argument('--topic', help='特定主题')
    parser.add_argument('--stocks', help='特定股票代码(逗号分隔)')
    parser.add_argument('--today', action='store_true', help='今日事件')
    parser.add_argument('--tier', type=int, help='特定级别')
    
    args = parser.parse_args()
    
    monitor = CatalystMonitor()
    
    if args.command == 'start':
        stocks = args.stocks.split(',') if args.stocks else None
        monitor.start(topic=args.topic, stocks=stocks)
    
    elif args.command == 'scan':
        monitor.scan()
    
    elif args.command == 'analyze':
        if not args.topic:
            print("❌ 请指定主题: --topic '主题名称'")
            sys.exit(1)
        monitor.analyze(args.topic)
    
    elif args.command == 'daily-report':
        monitor.daily_report()
    
    elif args.command == 'status':
        monitor.status()
    
    elif args.command == 'events':
        monitor.events(today=args.today, tier=args.tier)


if __name__ == '__main__':
    main()
