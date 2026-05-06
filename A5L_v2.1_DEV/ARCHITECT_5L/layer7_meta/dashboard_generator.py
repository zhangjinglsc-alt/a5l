#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L Web可视化仪表板
使用Streamlit快速搭建

功能：
1. 系统状态概览
2. 持仓监控
3. 信号追踪
4. 绩效图表
5. 告警展示
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

# 生成Streamlit应用代码
DASHBOARD_CODE = '''
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 页面配置
st.set_page_config(
    page_title="ARCHITECT-5L 投资系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .status-healthy {
        color: #00cc00;
        font-weight: bold;
    }
    .status-warning {
        color: #ff9900;
        font-weight: bold;
    }
    .status-critical {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """加载系统数据"""
    workspace = "/workspace/projects/workspace"
    
    data = {
        "portfolio": {},
        "signals": [],
        "alerts": [],
        "metrics": {}
    }
    
    # 尝试加载各种数据文件
    try:
        # 加载告警历史
        alert_file = f"{workspace}/data/architect_5l/alert_history.json"
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                data["alerts"] = json.load(f)[-50:]  # 最近50条
    except:
        pass
    
    # 模拟持仓数据（实际应从数据库加载）
    data["portfolio"] = {
        "total_equity": 1000000,
        "available_cash": 500000,
        "positions": [
            {"symbol": "000001.SZ", "name": "平安银行", "shares": 10000, "avg_cost": 10.5, "current": 11.2, "pnl": 7000},
            {"symbol": "000002.SZ", "name": "万科A", "shares": 5000, "avg_cost": 15.0, "current": 14.8, "pnl": -1000},
        ]
    }
    
    # 模拟信号数据
    data["signals"] = [
        {"timestamp": "2026-05-02 10:30:00", "symbol": "000001.SZ", "action": "BUY", "confidence": 0.85, "strategy": "stock_wizard"},
        {"timestamp": "2026-05-02 11:15:00", "symbol": "000858.SZ", "action": "BUY", "confidence": 0.72, "strategy": "trend_rs"},
    ]
    
    return data

def render_header():
    """渲染头部"""
    st.markdown('<p class="main-header">📊 ARCHITECT-5L 投资系统</p>', unsafe_allow_html=True)
    st.markdown(f"**系统时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 系统状态
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("系统状态", "🟢 健康", "+2%")
    with col2:
        st.metric("今日信号", "12", "+5")
    with col3:
        st.metric("持仓盈亏", "+¥6,000", "+1.2%")
    with col4:
        st.metric("风险敞口", "15%", "-2%")

def render_portfolio(data):
    """渲染持仓面板"""
    st.header("💼 持仓监控")
    
    portfolio = data.get("portfolio", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("资产概览")
        total = portfolio.get("total_equity", 0)
        cash = portfolio.get("available_cash", 0)
        invested = total - cash
        
        fig = go.Figure(data=[go.Pie(
            labels=['现金', '持仓'],
            values=[cash, invested],
            hole=.4,
            marker_colors=['#ff9999', '#66b3ff']
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("持仓明细")
        positions = portfolio.get("positions", [])
        if positions:
            df = pd.DataFrame(positions)
            df['pnl_color'] = df['pnl'].apply(lambda x: '🟢' if x > 0 else '🔴')
            st.dataframe(df[['symbol', 'name', 'shares', 'current', 'pnl_color', 'pnl']], use_container_width=True)

def render_signals(data):
    """渲染信号面板"""
    st.header("🎯 信号追踪")
    
    signals = data.get("signals", [])
    
    if signals:
        df = pd.DataFrame(signals)
        
        # 信号强度图表
        fig = px.bar(
            df,
            x='symbol',
            y='confidence',
            color='action',
            title='今日交易信号置信度',
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 信号列表
        st.subheader("最新信号")
        for signal in signals[-5:]:
            action_color = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "⚪"
            st.write(f"{action_color} **{signal['symbol']}** | {signal['action']} | 置信度: {signal['confidence']:.0%} | 策略: {signal['strategy']}")

def render_alerts(data):
    """渲染告警面板"""
    st.header("🚨 系统告警")
    
    alerts = data.get("alerts", [])
    
    if alerts:
        # 统计
        recent_alerts = [a for a in alerts if 
                        (datetime.now() - datetime.fromisoformat(a['timestamp'])).days < 1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("24h告警", len(recent_alerts))
        with col2:
            critical = len([a for a in recent_alerts if a['level'] == 'CRITICAL'])
            st.metric("严重", critical, delta_color="inverse")
        with col3:
            auto_fixed = len([a for a in recent_alerts if a['status'] == 'resolved'])
            st.metric("自动修复", auto_fixed)
        with col4:
            st.metric("待处理", len(recent_alerts) - auto_fixed)
        
        # 告警列表
        st.subheader("最近告警")
        for alert in alerts[-10:]:
            level_color = "🔴" if alert['level'] == 'CRITICAL' else "🟠" if alert['level'] == 'ERROR' else "🟡"
            status_icon = "✅" if alert['status'] == 'resolved' else "🔧" if alert['status'] == 'fixing' else "⚠️"
            
            with st.expander(f"{level_color} [{alert['timestamp'][:16]}] {alert['component']}"):
                st.write(f"**消息**: {alert['message']}")
                st.write(f"**级别**: {alert['level']}")
                st.write(f"**状态**: {status_icon} {alert['status']}")
                if alert.get('fix_result'):
                    st.write(f"**修复结果**: {alert['fix_result']}")
    else:
        st.info("✅ 最近24小时无告警")

def render_system_health():
    """渲染系统健康度"""
    st.header("🏥 系统健康")
    
    # 模拟各层健康状态
    layers = [
        {"name": "Layer 1: 数据底座", "status": "healthy", "latency": "12ms"},
        {"name": "Layer 2: 策略引擎", "status": "healthy", "latency": "5ms"},
        {"name": "Layer 3: 非结构化分析", "status": "healthy", "latency": "45ms"},
        {"name": "Layer 4: 决策信号", "status": "healthy", "latency": "3ms"},
        {"name": "Layer 5: 复盘进化", "status": "healthy", "latency": "8ms"},
    ]
    
    for layer in layers:
        status_color = "🟢" if layer['status'] == 'healthy' else "🟡" if layer['status'] == 'degraded' else "🔴"
        st.write(f"{status_color} **{layer['name']}** - 延迟: {layer['latency']}")

def main():
    """主函数"""
    # 加载数据
    data = load_data()
    
    # 侧边栏
    with st.sidebar:
        st.header("📊 ARCHITECT-5L")
        st.markdown("---")
        
        # 导航
        page = st.radio(
            "导航",
            ["系统概览", "持仓监控", "信号追踪", "告警中心", "系统健康"]
        )
        
        st.markdown("---")
        
        # 快速操作
        st.subheader("快速操作")
        if st.button("🔄 刷新数据"):
            st.experimental_rerun()
        if st.button("📥 生成报告"):
            st.info("报告生成功能开发中...")
        
        st.markdown("---")
        st.caption("v1.0 | ARCHITECT-5L Investment System")
    
    # 主内容区
    if page == "系统概览":
        render_header()
        col1, col2 = st.columns(2)
        with col1:
            render_portfolio(data)
        with col2:
            render_signals(data)
        render_alerts(data)
    
    elif page == "持仓监控":
        render_portfolio(data)
    
    elif page == "信号追踪":
        render_signals(data)
    
    elif page == "告警中心":
        render_alerts(data)
    
    elif page == "系统健康":
        render_system_health()

if __name__ == "__main__":
    main()
'''

def generate_dashboard():
    """生成仪表板代码文件"""
    dashboard_path = "/workspace/projects/workspace/ARCHITECT_5L/dashboard/app.py"
    os.makedirs(os.path.dirname(dashboard_path), exist_ok=True)
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(DASHBOARD_CODE)
    
    return dashboard_path

def create_requirements():
    """创建requirements.txt"""
    requirements = """streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
psutil>=5.9.0
feedparser>=6.0.10
requests>=2.31.0
akshare>=1.11.0
"""
    
    req_path = "/workspace/projects/workspace/ARCHITECT_5L/dashboard/requirements.txt"
    with open(req_path, 'w') as f:
        f.write(requirements)
    
    return req_path

def create_startup_script():
    """创建启动脚本"""
    script = """#!/bin/bash
# ARCHITECT-5L 仪表板启动脚本

echo "🚀 启动 ARCHITECT-5L Web仪表板..."

# 检查streamlit是否安装
if ! command -v streamlit &> /dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 启动仪表板
echo "🌐 仪表板地址: http://localhost:8501"
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
"""
    
    script_path = "/workspace/projects/workspace/ARCHITECT_5L/dashboard/start_dashboard.sh"
    with open(script_path, 'w') as f:
        f.write(script)
    
    # 添加执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

def demo():
    """演示可视化仪表板"""
    print("=" * 70)
    print("📊 Web可视化仪表板生成")
    print("=" * 70)
    
    # 生成文件
    dashboard_file = generate_dashboard()
    print(f"\n✅ 仪表板代码: {dashboard_file}")
    
    req_file = create_requirements()
    print(f"✅ 依赖文件: {req_file}")
    
    script_file = create_startup_script()
    print(f"✅ 启动脚本: {script_file}")
    
    print("\n" + "=" * 70)
    print("🚀 启动仪表板")
    print("=" * 70)
    print("\n执行以下命令启动Web界面:")
    print(f"  cd /workspace/projects/workspace/ARCHITECT_5L/dashboard")
    print(f"  ./start_dashboard.sh")
    print(f"\n或:")
    print(f"  cd /workspace/projects/workspace/ARCHITECT_5L/dashboard")
    print(f"  streamlit run app.py")
    print(f"\n访问地址: http://localhost:8501")
    
    print("\n" + "=" * 70)
    print("✅ 可视化仪表板已生成！")
    print("=" * 70)
    
    print("\n功能特性:")
    print("  • 系统概览面板")
    print("  • 持仓实时监控")
    print("  • 交易信号追踪")
    print("  • 告警中心")
    print("  • 系统健康度")
    print("  • 交互式图表（Plotly）")

if __name__ == "__main__":
    demo()
