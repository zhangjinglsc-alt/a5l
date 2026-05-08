#!/usr/bin/env python3
"""
A5L 研报学习系统 - 华创交运中东冲突与油轮运价研报
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
from process_manager import log_execution_start, log_execution_complete, log_learning

def analyze_huachuang_report():
    """分析华创交运研报"""
    
    # 开始执行记录
    exec_record = log_execution_start(
        task_name="analyze_huachuang_report",
        task_version="1.0.0",
        inputs={
            "source": "华创证券交运团队",
            "date": "2026-05-08",
            "topic": "中东冲突进展、油轮运价与海峡通行速递",
            "image_path": "/workspace/projects/media/inbound/15b5a6f5-3b3a-47ac-bad6-4aa92b21ce97.png"
        }
    )
    
    print("="*70)
    print("📚 华创交运研报学习".center(60))
    print("="*70)
    print(f"\n来源: 华创证券交运团队")
    print(f"日期: 2026-05-08")
    print(f"主题: 中东冲突进展、油轮运价与海峡通行速递")
    
    # 研报内容结构化提取
    report_content = {
        "title": "【华创交运】中东冲突进展、油轮运价与海峡通行速递",
        "date": "2026-05-08",
        "source": "华创证券"
    }
    
    # 提取核心知识点
    knowledge_items = []
    
    # 1. 中东冲突进展
    knowledge_items.append({
        "type": "geopolitical_event",
        "category": "middle_east_conflict",
        "content": "美伊临时协议接近达成：三阶段方案（停火→海峡危机解决→30天谈判窗口）",
        "source": "华创交运研报",
        "confidence": 0.75,
        "metadata": {
            "conflict_parties": ["美国", "伊朗"],
            "strait": "霍尔木兹海峡",
            "agreement_status": "接近达成临时协议",
            "phases": 3,
            "key_issues": ["核活动暂停", "导弹计划限制", "代理人支持停止"]
        }
    })
    
    # 2. 海峡通行数据 - 这是关键数据！
    knowledge_items.append({
        "type": "market_data",
        "category": "shipping_volume",
        "content": "霍尔木兹海峡通行量暴跌：5月7日仅1艘次，7日均6艘次，冲突前日均120艘次（-95%）",
        "source": "华创交运研报",
        "confidence": 0.95,
        "metadata": {
            "strait": "霍尔木兹海峡",
            "date_20260507": 1,  # 艘次
            "7day_avg": 6,
            "mar_apr_avg": 9,
            "pre_conflict_avg": 120,
            "decline_pct": -99.2  # (1-120)/120
        }
    })
    
    # 3. 油轮运价数据
    knowledge_items.append({
        "type": "market_data",
        "category": "shipping_rates",
        "content": "VLCC TD3C（波斯湾-中国）WS点458.8，日环比持平，换算运价46万美元/天",
        "source": "华创交运研报",
        "confidence": 0.95,
        "metadata": {
            "vlcc_td3c_ws": 458.8,
            "vlcc_td3c_rate": 46,  # 万美元/天
            "vlcc_td15_ws": 147.6,
            "vlcc_td15_rate": 10.9,
            "suezmax_td20_ws": 195.6,
            "aframax_td8_ws": 419.3
        }
    })
    
    # 4. 投资影响分析
    knowledge_items.append({
        "type": "investment_insight",
        "category": "shipping_sector",
        "content": "招商南油持仓风险：海峡通行量暴跌95%，若冲突缓解运价可能回调",
        "source": "研报分析",
        "confidence": 0.70,
        "metadata": {
            "affected_stock": "招商南油",
            "position_type": "真实持仓",
            "position_size": "1,220,600股",
            "accounts": ["WGB", "王力", "老娘"],
            "risk_factors": ["海峡通行量暴跌", "美伊协议接近达成", "运价高位风险"]
        }
    })
    
    # 5. 油价影响
    knowledge_items.append({
        "type": "market_data",
        "category": "oil_price",
        "content": "WTI原油深V反弹：跌超5%后反弹收涨1.45%，报99.27美元/桶",
        "source": "华创交运研报",
        "confidence": 0.90,
        "metadata": {
            "wti_price": 99.27,
            "daily_change_pct": 1.45,
            "intraday_volatility": "跌超5%后反弹"
        }
    })
    
    print(f"\n✅ 提取 {len(knowledge_items)} 个核心知识点")
    
    # 记录学习
    learn_record = log_learning(
        skill_id="industry_research",
        skill_version="4.0.0",
        source_type="research_report",
        source_id="huachuang_shipping_20260508",
        source_name="华创交运-中东冲突与油轮运价",
        source_content=json.dumps(report_content, ensure_ascii=False),
        knowledge_items=knowledge_items,
        proficiency_before=0.85,
        proficiency_after=0.855
    )
    
    print(f"✅ 学习记录ID: {learn_record.learning_id}")
    print(f"✅ SKILL: industry_research +0.5%")
    
    # 同时记录到持仓风险监控
    log_learning(
        skill_id="risk_management",
        skill_version="1.0.0",
        source_type="market_intelligence",
        source_id="huachuang_shipping_20260508",
        source_name="招商南油持仓风险更新",
        source_content="海峡通行量暴跌95%，美伊协议接近达成，运价高位风险",
        knowledge_items=[knowledge_items[3]],  # 只传投资影响
        proficiency_before=0.75,
        proficiency_after=0.752
    )
    
    print(f"✅ SKILL: risk_management +0.2%")
    
    # 生成学习摘要
    summary = {
        "report_info": {
            "title": "【华创交运】中东冲突进展、油轮运价与海峡通行速递",
            "source": "华创证券交运团队",
            "date": "2026-05-08"
        },
        "key_findings": [
            "美伊临时协议接近达成（三阶段方案）",
            "霍尔木兹海峡通行量暴跌95%（1艘次 vs 冲突前120艘次）",
            "VLCC运价维持高位（TD3C: 46万美元/天）",
            "WTI原油深V反弹至99.27美元",
            "招商南油持仓风险上升"
        ],
        "critical_data": {
            "strait_transits": {
                "current": 1,
                "pre_conflict": 120,
                "decline": "-99.2%"
            },
            "vlcc_rates": {
                "td3c_ws": 458.8,
                "td3c_usd_per_day": 46
            },
            "wti_price": 99.27
        },
        "investment_implications": {
            "招商南油": {
                "position": "1,220,600股（跨三账户）",
                "risk_level": "高",
                "risk_factors": [
                    "海峡通行量暴跌95%",
                    "美伊协议若达成运价可能回调",
                    "持仓过度集中（70.7%）"
                ],
                "suggested_action": "考虑减仓锁定利润，或设置止盈止损"
            }
        },
        "knowledge_items": len(knowledge_items),
        "skills_updated": ["industry_research", "risk_management"]
    }
    
    # 完成执行记录
    log_execution_complete(
        exec_record,
        status="success",
        outputs=summary,
        metrics={
            "knowledge_items": len(knowledge_items),
            "skills_updated": 2,
            "proficiency_gain": 0.007
        },
        processing={
            "steps_completed": ["parse_report", "extract_data", "analyze_impact", "log_learning"],
            "data_categories": ["geopolitical", "shipping_volume", "rates", "oil_price", "investment_risk"]
        }
    )
    
    print("\n" + "="*70)
    print("✅ 研报学习完成，知识已入库".center(60))
    print("="*70)
    
    return summary

if __name__ == "__main__":
    summary = analyze_huachuang_report()
    
    print("\n📊 学习摘要:")
    print(f"   研报: {summary['report_info']['title']}")
    print(f"   知识点: {summary['knowledge_items']} 个")
    print(f"   更新SKILL: {', '.join(summary['skills_updated'])}")
    
    print("\n🚨 关键风险提示:")
    print(f"   标的: 招商南油")
    print(f"   持仓: {summary['investment_implications']['招商南油']['position']}")
    print(f"   风险: 海峡通行量暴跌99.2%，美伊协议接近达成")
    print(f"   建议: 考虑减仓锁定利润")
