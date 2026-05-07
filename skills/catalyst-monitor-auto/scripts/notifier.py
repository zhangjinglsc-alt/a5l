#!/usr/bin/env python3
"""
Notifier - 推送通知器
将催化事件推送到飞书
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, '/workspace/projects/workspace')

class FeishuNotifier:
    """飞书推送通知器"""
    
    def __init__(self):
        self.base_path = Path('/workspace/projects/workspace/skills/catalyst-monitor-auto')
    
    def notify(self, title, content, tier=3):
        """
        推送通知到飞书
        
        Args:
            title: 通知标题
            content: 通知内容
            tier: 事件级别 (影响推送方式)
        """
        # 根据级别决定推送方式
        if tier == 1:
            priority = "🔴 紧急"
            full_title = f"{priority} {title}"
        elif tier == 2:
            priority = "🟠 重要"
            full_title = f"{priority} {title}"
        elif tier == 3:
            priority = "🟡 关注"
            full_title = f"{priority} {title}"
        else:
            priority = "⚪ 一般"
            full_title = f"{priority} {title}"
        
        # 构建消息
        message = f"""
{full_title}
{'='*50}
{content}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
来源: Catalyst Monitor Auto
"""
        
        # 保存到本地文件 (实际实现将调用飞书API)
        self._save_notification(message)
        
        print(f"📤 推送通知: {title} (Tier {tier})")
        
        # 这里将实际调用飞书消息API
        # 由于安全限制，暂时只打印到控制台和保存到文件
        # 实际部署时需要集成feishu_im_user_message工具
    
    def _save_notification(self, message):
        """保存通知到本地"""
        notify_path = self.base_path / 'data' / 'notifications'
        notify_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"notify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(notify_path / filename, 'w', encoding='utf-8') as f:
            f.write(message)
    
    def send_tier1_alert(self, event):
        """发送Tier 1紧急提醒"""
        content = f"""
🎯 Tier 1 范式级催化事件！

事件: {event.get('title', '')}
分级: Tier 1 (置信度: {event.get('confidence', 'medium')})
理由: {event.get('reason', '')}

💰 仓位建议:
├─ 仓位上限: {event.get('position_limit', '20-25%')}
├─ 持有周期: {event.get('holding_period', '季度→年度')}
└─ 操作建议: {event.get('action', '')}

⚠️ 重要提示:
• 立即调整主仓位
• 寻找预期差入口 (分销商/上游/替代品)
• 不追龙一涨停
• 逻辑证伪才卖出

详细分析请查看完整报告。
"""
        self.notify("Tier 1 范式级催化事件", content, tier=1)
    
    def send_tier2_alert(self, event):
        """发送Tier 2重要提醒"""
        content = f"""
🔶 Tier 2 周期确认级事件

事件: {event.get('title', '')}
分级: Tier 2 (置信度: {event.get('confidence', 'medium')})
理由: {event.get('reason', '')}

💰 仓位建议:
├─ 仓位上限: {event.get('position_limit', '15-20%')}
├─ 持有周期: {event.get('holding_period', '月度→季度')}
└─ 操作建议: {event.get('action', '')}

💡 提示: Tier 1 + Tier 2 共振 = 最强共振
"""
        self.notify("Tier 2 周期确认级事件", content, tier=2)
    
    def send_daily_summary(self, events):
        """发送每日汇总"""
        # 统计各级别数量
        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for e in events:
            tier_counts[e.get('tier', 4)] += 1
        
        content = f"""
📊 催化事件每日汇总

今日事件统计:
├─ 🎯 Tier 1: {tier_counts[1]} 个
├─ 🔶 Tier 2: {tier_counts[2]} 个
├─ 🔷 Tier 3: {tier_counts[3]} 个
└─ ⚪ Tier 4: {tier_counts[4]} 个

重点事件:
"""
        
        for e in events[:5]:
            tier_icon = {1: "🎯", 2: "🔶", 3: "🔷", 4: "⚪"}
            icon = tier_icon.get(e.get('tier', 4), "⚪")
            content += f"\n{icon} [{e.get('tier', '?')}] {e.get('title', '未知')[:30]}"
        
        self.notify("催化事件日报", content, tier=3)


def main():
    """命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='推送通知')
    parser.add_argument('title', help='通知标题')
    parser.add_argument('content', help='通知内容')
    parser.add_argument('--tier', type=int, default=3, help='事件级别')
    
    args = parser.parse_args()
    
    notifier = FeishuNotifier()
    notifier.notify(args.title, args.content, args.tier)
    print("✅ 通知已发送")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main()
    else:
        # 测试通知
        notifier = FeishuNotifier()
        notifier.notify("测试通知", "催化事件监控系统测试消息", tier=3)
