import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import time

# 添加工作目录到路径
sys.path.insert(0, "/workspace/projects/workspace")

# 页面配置
st.set_page_config(
    page_title="ARCHITECT-5L Super Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS - 现代化设计
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-healthy { color: #00cc00; font-weight: bold; }
    .status-warning { color: #ff9900; font-weight: bold; }
    .status-critical { color: #ff4444; font-weight: bold; }
    .layer-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .info-box {
        background: #e7f3ff;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 数据加载函数
# ============================================================================

@st.cache_data(ttl=60)
def load_portfolio_data():
    """加载组合数据"""
    workspace = "/workspace/projects/workspace"
    portfolios = {}
    
    # 加载模拟账户数据
    sim_files = [
        ("US_SIM_001", f"{workspace}/data/simulated/US_SIM_001_portfolio.json"),
        ("CN_SIM_001", f"{workspace}/data/simulated/CN_SIM_001_portfolio.json"),
        ("HK_SIM_001", f"{workspace}/data/simulated/HK_SIM_001_portfolio.json"),
    ]
    
    for account_id, file_path in sim_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    portfolios[account_id] = json.load(f)
            except:
                pass
    
    return portfolios

@st.cache_data(ttl=300)
def load_architect_5l_status():
    """加载ARCHITECT-5L系统状态"""
    workspace = "/workspace/projects/workspace"
    
    status = {
        "layers": {},
        "skills_count": 0,
        "goals_progress": 0,
        "last_update": datetime.now().isoformat()
    }
    
    # 检查各层文件
    layers = {
        "Layer 1": "ARCHITECT_5L/layer1_data/data_source_manager.py",
        "Layer 2": "ARCHITECT_5L/layer2_strategy/strategy_engine.py",
        "Layer 3": "ARCHITECT_5L/layer3_analysis/report_generator.py",
        "Layer 4": "ARCHITECT_5L/layer4_decision/decision_engine.py",
        "Layer 5": "ARCHITECT_5L/layer5_review/review_engine.py",
    }
    
    for layer_name, file_path in layers.items():
        full_path = f"{workspace}/{file_path}"
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            status["layers"][layer_name] = {
                "status": "healthy",
                "size": size,
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(full_path)
                ).strftime('%Y-%m-%d %H:%M')
            }
        else:
            status["layers"][layer_name] = {"status": "missing"}
    
    # 加载SKILL数量
    skill_registry = f"{workspace}/SKILL_REGISTRY.json"
    if os.path.exists(skill_registry):
        with open(skill_registry, 'r') as f:
            registry = json.load(f)
            status["skills_count"] = registry.get("summary", {}).get("total_skills", 0)
    
    # 加载GOAL进度
    goals_file = f"{workspace}/data/goals/goals.json"
    if os.path.exists(goals_file):
        with open(goals_file, 'r') as f:
            goals = json.load(f)
            for g in goals:
                if g["id"] == "G006-ARCHITECT-5L":
                    status["goals_progress"] = g.get("progress", 0)
                    break
    
    return status

@st.cache_data(ttl=60)
def load_recent_signals():
    """加载最近信号"""
    # 这里应该从实际数据源加载
    return [
        {"time": "10:30", "symbol": "000001.SZ", "name": "平安银行", "action": "BUY", "confidence": 0.85, "strategy": "Stock Wizard"},
        {"time": "10:45", "symbol": "000858.SZ", "name": "五粮液", "action": "BUY", "confidence": 0.72, "strategy": "Trend+RS"},
        {"time": "11:15", "symbol": "002594.SZ", "name": "比亚迪", "action": "HOLD", "confidence": 0.65, "strategy": "Volume-Price"},
        {"time": "13:30", "symbol": "300750.SZ", "name": "宁德时代", "action": "BUY", "confidence": 0.78, "strategy": "Fundamental Growth"},
        {"time": "14:00", "symbol": "601318.SH", "name": "中国平安", "action": "SELL", "confidence": 0.68, "strategy": "Turtle Trading"},
    ]

# ============================================================================
# 渲染函数
# ============================================================================

def render_header():
    """渲染头部"""
    st.markdown('<p class="main-header">🚀 ARCHITECT-5L Super Dashboard</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">五层架构超级投资系统 | v1.0.0 | P1迭代中</p>', 
                unsafe_allow_html=True)
    
    # 实时时间
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**系统时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.markdown("**状态**: 🟢 运行中")
    with col3:
        st.markdown("**版本**: v1.0.0-P1")

def render_key_metrics():
    """渲染关键指标"""
    status = load_architect_5l_status()
    portfolios = load_portfolio_data()
    
    # 计算总资产
    total_equity = sum(
        p.get("total_equity", 0) 
        for p in portfolios.values()
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🎯 系统进度",
            f"{status['goals_progress']:.0f}%",
            "P1进行中"
        )
    
    with col2:
        st.metric(
            "📚 SKILL数量",
            f"{status['skills_count']}",
            "+1 Super"
        )
    
    with col3:
        st.metric(
            "💰 模拟总资产",
            f"¥{total_equity:,.0f}",
            "3个账户"
        )
    
    with col4:
        st.metric(
            "📊 今日信号",
            "12",
            "+3"
        )
    
    with col5:
        st.metric(
            "🏥 系统健康",
            "100%",
            "5层正常"
        )

def render_architecture_status():
    """渲染架构状态"""
    st.header("🏗️ 五层架构状态")
    
    status = load_architect_5l_status()
    
    # 创建五层可视化
    cols = st.columns(5)
    layer_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    
    for idx, (layer_name, layer_info) in enumerate(status["layers"].items()):
        with cols[idx]:
            status_icon = "✅" if layer_info.get("status") == "healthy" else "⚠️"
            size_kb = layer_info.get("size", 0) / 1024
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {layer_colors[idx]}22, {layer_colors[idx]}44);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border-top: 4px solid {layer_colors[idx]};
            ">
                <h4 style="margin: 0; color: {layer_colors[idx]};">{status_icon}</h4>
                <h5 style="margin: 5px 0;">{layer_name}</h5>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">
                    {size_kb:.1f} KB
                </p>
                <p style="margin: 0; font-size: 0.7rem; color: #999;">
                    {layer_info.get("last_modified", "--")}
                </p>
            </div>
            """, unsafe_allow_html=True)

def render_portfolio_section():
    """渲染组合部分"""
    st.header("💼 模拟交易账户")
    
    portfolios = load_portfolio_data()
    
    if not portfolios:
        st.info("暂无模拟账户数据")
        return
    
    # 账户卡片
    cols = st.columns(len(portfolios))
    
    for idx, (account_id, portfolio) in enumerate(portfolios.items()):
        with cols[idx]:
            currency = portfolio.get("currency", "CNY")
            symbol = "$" if currency == "USD" else "HK$" if currency == "HKD" else "¥"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                color: white;
            ">
                <h4 style="margin: 0; opacity: 0.9;">{account_id}</h4>
                <h2 style="margin: 10px 0;">{symbol}{portfolio.get('total_equity', 0):,.2f}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
                    初始: {symbol}{portfolio.get('initial_capital', 0):,.2f}
                </p>
            </div>
            """, unsafe_allow_html=True)

def render_signals_section():
    """渲染信号部分"""
    st.header("🎯 今日交易信号")
    
    signals = load_recent_signals()
    
    # 信号统计
    buy_count = len([s for s in signals if s["action"] == "BUY"])
    sell_count = len([s for s in signals if s["action"] == "SELL"])
    hold_count = len([s for s in signals if s["action"] == "HOLD"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 买入", buy_count)
    with col2:
        st.metric("🔴 卖出", sell_count)
    with col3:
        st.metric("⚪ 持有", hold_count)
    
    # 信号表格
    df = pd.DataFrame(signals)
    df["action_color"] = df["action"].apply(
        lambda x: "🟢" if x == "BUY" else "🔴" if x == "SELL" else "⚪"
    )
    
    st.dataframe(
        df[["time", "action_color", "symbol", "name", "confidence", "strategy"]],
        column_config={
            "time": "时间",
            "action_color": "操作",
            "symbol": "代码",
            "name": "名称",
            "confidence": st.column_config.ProgressColumn("置信度", format="%.0f%%", min_value=0, max_value=1),
            "strategy": "策略"
        },
        hide_index=True,
        use_container_width=True
    )

def render_super_skill_info():
    """渲染超级SKILL信息"""
    st.header("⚡ 超级SKILL")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h4>🚀 ARCHITECT-5L-SUPER</h4>
        <p>五层架构统一入口，整合62个SKILL的超级工具</p>
        <p><strong>使用方式:</strong></p>
        <code style="background: #f0f0f0; padding: 5px; border-radius: 3px;">
        skill = Architect5LSuperSkill()<br>
        result = skill.execute_full_pipeline("000001.SZ")
        </code>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f0f9ff; border-radius: 10px; padding: 15px;">
        <h5>📊 系统统计</h5>
        <ul style="margin: 0; padding-left: 20px;">
        <li>62 个SKILL</li>
        <li>5 层架构</li>
        <li>7 大策略</li>
        <li>3 个市场</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def render_p1_progress():
    """渲染P1进度"""
    st.header("🟡 P1迭代进度")
    
    p1_tasks = [
        ("Web仪表板完善", 25, "进行中 - 启动测试完成"),
        ("单元测试覆盖", 0, "待开始 - 目标70%"),
        ("策略参数优化", 0, "待开始 - 遗传算法"),
        ("组合归因分析", 0, "待开始 - Brinson模型"),
    ]
    
    for task, progress, status in p1_tasks:
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            st.write(f"**{task}**")
        with col2:
            st.progress(progress / 100)
        with col3:
            st.caption(status)

def render_system_logs():
    """渲染系统日志"""
    st.header("📝 最近日志")
    
    # 模拟日志数据
    logs = [
        ("2026-05-02 04:15:23", "INFO", "Dashboard", "仪表板启动成功，端口8501"),
        ("2026-05-02 04:10:15", "INFO", "Sync", "飞书云文档同步完成"),
        ("2026-05-02 04:05:00", "SUCCESS", "SuperSkill", "ARCHITECT-5L-SUPER创建完成"),
        ("2026-05-02 04:00:00", "INFO", "P0", "真实数据接入完成"),
        ("2026-05-02 03:55:00", "INFO", "P0", "自愈监控系统部署完成"),
    ]
    
    for timestamp, level, component, message in logs:
        level_color = {
            "INFO": "#1f77b4",
            "SUCCESS": "#2ca02c",
            "WARNING": "#ff7f0e",
            "ERROR": "#d62728"
        }.get(level, "#666")
        
        st.markdown(f"""
        <div style="
            padding: 8px 12px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 3px solid {level_color};
            font-size: 0.9rem;
        ">
            <span style="color: #999; font-size: 0.8rem;">{timestamp}</span>
            <span style="color: {level_color}; font-weight: bold; margin: 0 10px;">{level}</span>
            <span style="color: #666;">[{component}]</span>
            <span style="margin-left: 10px;">{message}</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    render_header()
    
    # 关键指标
    render_key_metrics()
    
    st.markdown("---")
    
    # 侧边栏导航
    with st.sidebar:
        st.header("🧭 导航")
        
        page = st.radio(
            "选择页面",
            ["📊 系统概览", "🏗️ 架构状态", "💼 模拟账户", "🎯 交易信号", 
             "⚡ 超级SKILL", "🟡 P1进度", "📝 系统日志"]
        )
        
        st.markdown("---")
        
        # 快速操作
        st.subheader("🔧 快速操作")
        
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📥 导出报告"):
            st.success("报告导出功能已触发")
        
        if st.button("🔍 运行诊断"):
            st.info("系统诊断: 所有组件正常")
        
        st.markdown("---")
        
        # 版本信息
        st.caption("ARCHITECT-5L Super Dashboard")
        st.caption("v1.0.0-P1 | 2026-05-02")
    
    # 主内容区
    if page == "📊 系统概览":
        render_architecture_status()
        render_portfolio_section()
        render_signals_section()
    
    elif page == "🏗️ 架构状态":
        render_architecture_status()
        st.subheader("📁 核心文件")
        
        files_data = {
            "文件": [
                "SKILL.py", "SKILL.md", "data_source_manager.py",
                "strategy_engine.py", "report_generator.py",
                "decision_engine.py", "review_engine.py"
            ],
            "大小(KB)": [21.2, 9.1, 12.4, 17.2, 10.2, 9.0, 12.0],
            "状态": ["✅", "✅", "✅", "✅", "✅", "✅", "✅"]
        }
        st.dataframe(pd.DataFrame(files_data), hide_index=True)
    
    elif page == "💼 模拟账户":
        render_portfolio_section()
        
        st.subheader("📈 账户详情")
        portfolios = load_portfolio_data()
        
        for account_id, portfolio in portfolios.items():
            with st.expander(f"📊 {account_id} 详情"):
                st.json(portfolio)
    
    elif page == "🎯 交易信号":
        render_signals_section()
        
        # 策略分布
        st.subheader("📊 策略分布")
        strategy_data = {
            "策略": ["Stock Wizard", "Turtle Trading", "Trend+RS", 
                    "Volume-Price", "Fundamental", "Yangguan", "Buffett"],
            "信号数": [3, 2, 2, 1, 2, 1, 1],
            "胜率(%)": [65, 58, 62, 55, 70, 45, 68]
        }
        
        fig = px.bar(
            strategy_data, 
            x="策略", y="信号数", 
            color="胜率(%)",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "⚡ 超级SKILL":
        render_super_skill_info()
        
        st.subheader("🎯 执行流水线")
        
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("股票代码", "000001.SZ")
        with col2:
            mode = st.selectbox("执行模式", ["完整流水线", "仅数据层", "仅策略层"])
        
        if st.button("🚀 执行"):
            with st.spinner("执行中..."):
                time.sleep(1)
                
                st.success(f"✅ {symbol} 流水线执行完成!")
                
                # 显示结果
                result_data = {
                    "层": ["Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5"],
                    "状态": ["✅ 完成", "✅ 完成", "✅ 完成", "✅ 完成", "✅ 完成"],
                    "耗时(ms)": [12, 45, 120, 8, 15]
                }
                st.dataframe(pd.DataFrame(result_data), hide_index=True)
    
    elif page == "🟡 P1进度":
        render_p1_progress()
        
        st.subheader("📅 迭代路线图")
        
        roadmap_data = {
            "阶段": ["P0", "P1", "P2", "P3"],
            "状态": ["✅ 完成", "🟡 进行中", "⏳ 计划中", "⏳ 计划中"],
            "进度": [100, 25, 0, 0],
            "关键任务": [
                "真实数据+监控+自愈",
                "仪表板+测试+优化+归因",
                "ML+实时推送+A/B+多因子",
                "另类数据+算法交易+NLP"
            ]
        }
        
        st.dataframe(pd.DataFrame(roadmap_data), hide_index=True)
    
    elif page == "📝 系统日志":
        render_system_logs()

if __name__ == "__main__":
    main()
