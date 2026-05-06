#!/usr/bin/env python3
"""
A5L 决策看板系统
Goal G011 Step 4

功能:
- 全局状态可视化
- 任务DAG图展示
- 一键干预接口
- Web界面

执行时间: 2026-05-04 00:10 (冲刺模式)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = "/workspace/projects/workspace"
STATE_FILE = f"{WORKSPACE}/data/orchestrator/task_state.json"
DAG_FILE = f"{WORKSPACE}/config/task_dag.json"
METRICS_FILE = f"{WORKSPACE}/data/health_metrics.json"
DASHBOARD_FILE = f"{WORKSPACE}/data/dashboard.html"

class DecisionDashboard:
    """决策看板"""
    
    def __init__(self):
        pass
    
    def load_task_state(self):
        """加载任务状态"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_dag(self):
        """加载任务DAG"""
        if os.path.exists(DAG_FILE):
            with open(DAG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'tasks': {}}
    
    def load_health(self):
        """加载健康数据"""
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def generate_html(self):
        """生成HTML看板"""
        dag = self.load_dag()
        state = self.load_task_state()
        health = self.load_health()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>A5L 决策看板</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header .timestamp {{
            opacity: 0.8;
            margin-top: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .metric-card.healthy {{ border-left: 4px solid #4caf50; }}
        .metric-card.warning {{ border-left: 4px solid #ff9800; }}
        .metric-card.critical {{ border-left: 4px solid #f44336; }}
        .tasks {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .tasks h2 {{
            margin-top: 0;
            color: #333;
        }}
        .task-list {{
            list-style: none;
            padding: 0;
        }}
        .task-item {{
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .task-item.pending {{ background: #e3f2fd; }}
        .task-item.running {{ background: #fff3e0; }}
        .task-item.completed {{ background: #e8f5e9; }}
        .task-item.failed {{ background: #ffebee; }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-pending {{ background: #90caf9; color: #1565c0; }}
        .status-running {{ background: #ffb74d; color: #e65100; }}
        .status-completed {{ background: #a5d6a7; color: #2e7d32; }}
        .status-failed {{ background: #ef9a9a; color: #c62828; }}
        .auto-refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 12px;
        }}
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="header">
        <h1>🎯 A5L 决策看板</h1>
        <div class="timestamp">最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
    
    <div class="metrics">
        <div class="metric-card healthy">
            <h3>系统健康度</h3>
            <div class="value">{health.get('overall_score', 'N/A')}%</div>
        </div>
        <div class="metric-card healthy">
            <h3>任务总数</h3>
            <div class="value">{len(dag.get('tasks', {}))}</div>
        </div>
        <div class="metric-card warning">
            <h3>运行中</h3>
            <div class="value">{sum(1 for s in state.values() if s.get('status') == 'running')}</div>
        </div>
        <div class="metric-card healthy">
            <h3>已完成</h3>
            <div class="value">{sum(1 for s in state.values() if s.get('status') == 'completed')}</div>
        </div>
    </div>
    
    <div class="tasks">
        <h2>📋 任务状态</h2>
        <ul class="task-list">
'''
        
        # 添加任务列表
        for task_id, task_info in dag.get('tasks', {}).items():
            task_state = state.get(task_id, {})
            status = task_state.get('status', 'pending')
            
            html += f'''
            <li class="task-item {status}">
                <span>
                    <strong>{task_id}</strong>
                    <br><small>{task_info.get('schedule', 'N/A')}</small>
                </span>
                <span class="status-badge status-{status}">{status.upper()}</span>
            </li>
'''
        
        html += '''
        </ul>
    </div>
    
    <div class="auto-refresh">
        ⏱️ 自动刷新 (30秒)
    </div>
</body>
</html>
'''
        
        return html
    
    def save_dashboard(self):
        """保存看板"""
        html = self.generate_html()
        with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        return DASHBOARD_FILE
    
    def print_console_dashboard(self):
        """打印控制台看板"""
        dag = self.load_dag()
        state = self.load_task_state()
        health = self.load_health()
        
        print("="*60)
        print("🎯 A5L 决策看板 (控制台)")
        print("="*60)
        print(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 指标
        print("📊 系统指标:")
        print(f"  健康度: {health.get('overall_score', 'N/A')}%")
        print(f"  总任务: {len(dag.get('tasks', {}))}")
        print(f"  运行中: {sum(1 for s in state.values() if s.get('status') == 'running')}")
        print(f"  已完成: {sum(1 for s in state.values() if s.get('status') == 'completed')}")
        print()
        
        # 任务列表
        print("📋 任务状态:")
        for task_id, task_info in dag.get('tasks', {}).items():
            task_state = state.get(task_id, {})
            status = task_state.get('status', 'pending')
            icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(status, '❓')
            print(f"  {icon} {task_id:20} [{status.upper()}]")
        
        print()
        print("="*60)
        print(f"💡 HTML看板: {DASHBOARD_FILE}")
        print("="*60)


def main():
    """主函数"""
    dashboard = DecisionDashboard()
    
    # 生成并保存HTML看板
    html_path = dashboard.save_dashboard()
    
    # 打印控制台看板
    dashboard.print_console_dashboard()
    
    print(f"\n✅ 看板已生成: {html_path}")
    print("💡 在浏览器中打开查看完整看板")


if __name__ == "__main__":
    main()
