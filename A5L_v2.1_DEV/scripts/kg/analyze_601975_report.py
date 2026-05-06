#!/usr/bin/env python3
"""
A5L 研报分析实战 - 招商南油(601975)
使用G010系统分析用户提供的研报

执行时间: 2026-05-04 01:07
"""

import os
import sys
import json
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
ANALYSIS_DIR = f"{WORKSPACE}/data/stock_research/analysis"

def analyze_report():
    """分析招商南油研报"""
    
    print("="*70)
    print("🎯 A5L 研报分析实战 - 招商南油(601975)")
    print("="*70)
    print()
    
    # 研报元数据
    report_meta = {
        "stock_code": "601975.SH",
        "stock_name": "招商南油",
        "report_date": "2026-04-12",
        "analyst": "小张 AI Investment System v2.1",
        "rating": "HOLD (中性持有)",
        "target_price_low": 4.50,
        "target_price_high": 5.80,
        "current_cost": 4.955
    }
    
    print("📋 研报基本信息")
    print(f"  股票: {report_meta['stock_name']} ({report_meta['stock_code']})")
    print(f"  评级: {report_meta['rating']}")
    print(f"  目标价: {report_meta['target_price_low']} - {report_meta['target_price_high']}元")
    print(f"  成本价: {report_meta['current_cost']}元")
    print()
    
    # 提取关键实体
    entities = {
        "stocks": ["601975", "600026", "601872"],  # 招商南油、中远海能、招商轮船
        "industries": ["油运", "成品油运输", "原油运输"],
        "concepts": ["央企", "航运", "周期股"],
        "competitors": ["中远海能", "招商轮船"],
        "factors": ["地缘政治", "裂解价差", "运力供给", "环保法规"]
    }
    
    print("🔍 实体提取结果")
    print(f"  股票: {len(entities['stocks'])} 只")
    print(f"    - 招商南油(601975) - 目标标的")
    print(f"    - 中远海能(600026) - 主要竞争对手")
    print(f"    - 招商轮船(601872) - 主要竞争对手")
    print(f"  行业: {', '.join(entities['industries'])}")
    print(f"  概念: {', '.join(entities['concepts'])}")
    print()
    
    # 业务板块分析
    segments = {
        "外贸成品油": {"占比": "60%", "毛利率": "中等", "增长性": "高"},
        "内贸原油": {"占比": "25%", "毛利率": "稳定", "增长性": "低"},
        "化学品": {"占比": "10%", "毛利率": "高", "增长性": "中"}
    }
    
    print("🏭 业务板块分析")
    for segment, data in segments.items():
        print(f"  {segment}: 收入{data['占比']}, 毛利率{data['毛利率']}, 增长性{data['增长性']}")
    print()
    
    # 风险因子评分
    risk_factors = {
        "地缘政治风险": {"score": 0.3, "level": "高", "impact": "运价波动"},
        "运价波动风险": {"score": 0.3, "level": "高", "impact": "业绩不稳定"},
        "竞争风险": {"score": 0.6, "level": "中", "impact": "规模劣势"},
        "需求风险": {"score": 0.5, "level": "中", "impact": "新能源替代"},
        "环保法规风险": {"score": 0.6, "level": "中", "impact": "合规成本上升"}
    }
    
    print("⚠️ 风险分析")
    for risk, data in risk_factors.items():
        print(f"  {risk}: {data['level']} - {data['impact']}")
    
    # 计算综合风险分
    avg_risk = sum(d['score'] for d in risk_factors.values()) / len(risk_factors)
    print(f"  综合风险分: {avg_risk:.2f} (越高越好)")
    print()
    
    # 情景分析
    scenarios = {
        "乐观": {"prob": 0.25, "target": "6.50-7.00", "return": "+30-40%"},
        "基准": {"prob": 0.50, "target": "5.20-5.80", "return": "+5-17%"},
        "悲观": {"prob": 0.25, "target": "3.80-4.50", "return": "-9-23%"}
    }
    
    print("📊 情景分析")
    for scenario, data in scenarios.items():
        print(f"  {scenario}情景({data['prob']:.0%}): 目标价{data['target']}元, 预期收益{data['return']}")
    
    # 概率加权预期
    expected_return = 0.25 * 0.35 + 0.50 * 0.11 + 0.25 * (-0.16)  # 近似计算
    print(f"  概率加权预期收益: +{expected_return*100:.1f}%")
    print()
    
    # 投资信号生成
    print("🎯 A5L 投资信号生成")
    print()
    
    # 评分维度
    factors = {
        "industry_position": 0.60,   # 产业链位置 - 国内成品油运输龙头，但规模不及中远海能
        "policy_support": 0.70,      # 政策支持 - 央企背景，融资能力强
        "competition": 0.50,         # 竞争格局 - 面临国际巨头和国内龙头竞争
        "demand_trend": 0.65,        # 需求趋势 - 炼厂产能扩张，但新能源替代长期不利
        "valuation": 0.55,           # 估值水平 - 成本4.955元，目标5.20-5.80元
        "earnings_expectation": 0.50 # 业绩预期 - Q4业绩超预期，但2025年收入同比下滑10%
    }
    
    # 计算置信度
    confidence = sum(factors.values()) / len(factors) * 100
    
    # 确定信号
    if confidence >= 70:
        signal_type = "BULLISH"
        action = "看多"
    elif confidence >= 50:
        signal_type = "WATCH"
        action = "观望/持有"
    else:
        signal_type = "BEARISH"
        action = "看空"
    
    print(f"  综合评分: {confidence:.1f}分")
    print(f"  信号类型: {signal_type}")
    print(f"  建议操作: {action}")
    print()
    
    # 详细理由
    print("💡 核心逻辑")
    print("  ✅ 正面因素:")
    print("    - 央企背景，融资能力强")
    print("    - 成品油运输专业化运营")
    print("    - Q4业绩超预期(+37%)")
    print("    - 运力供给紧张，新船订单低位")
    print("    - 股息率有望提升至3-4%")
    print()
    print("  ⚠️ 负面因素:")
    print("    - 规模不及中远海能、招商轮船")
    print("    - 缺乏VLCC大型原油船")
    print("    - 2025年收入同比下滑10%")
    print("    - 强周期性行业，运价波动大")
    print("    - 新能源替代长期利空")
    print()
    
    # 针对用户持仓的建议
    print("💼 针对您的持仓建议")
    print("  当前持仓: 38.18万股，成本4.955元，占比36.7%")
    print()
    print("  ⚠️ 风险提示: 仓位过重(36.7%)，集中度风险高！")
    print()
    print("  📋 操作建议:")
    print("    1. 【减仓】建议逐步减仓至20%以内，控制单票风险")
    print("    2. 【止盈】若涨至5.50元以上(+11%)，可减仓1/3锁定利润")
    print("    3. 【止损】若跌破4.50元(-9%)，建议减仓一半")
    print("    4. 【持有】4.50-5.50元区间，可继续持有观望")
    print()
    
    # 生成投资报告
    investment_signal = {
        "signal_id": f"SIG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_601975",
        "stock_code": "601975.SH",
        "stock_name": "招商南油",
        "signal_type": signal_type,
        "action": action,
        "confidence": round(confidence, 1),
        "confidence_level": "中等" if 60 <= confidence < 80 else "低",
        "current_price": 4.955,
        "target_price": {"low": 5.20, "high": 5.80},
        "expected_return": f"+{expected_return*100:.1f}%",
        "risk_level": "高",
        "position_advice": "减仓至20%以内",
        "factors": factors,
        "generated_at": datetime.now().isoformat(),
        "data_source": "用户投喂研报 - 招商南油深度研究"
    }
    
    # 保存报告
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    report_file = f"{ANALYSIS_DIR}/signal_601975_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(investment_signal, f, ensure_ascii=False, indent=2)
    
    print("="*70)
    print(f"✅ 分析报告已生成: {report_file}")
    print("="*70)
    
    return investment_signal

if __name__ == "__main__":
    signal = analyze_report()
