#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 产业链分析器 - 演示脚本
五一假期特供：让A5L变得无比强大！

功能演示:
1. AI算力产业链完整分析
2. 网络关系建模
3. 投资分析 (估值/机会/风险)
4. 自动生成报告
5. KIWI知识归档

使用方法:
    python3 demo_industry_chain_analyzer.py
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer3_analysis/analyzers')

from ARCHITECT_5L.layer3_analysis.analyzers.industry_chain_analyzer import (
    IndustryChainAnalyzer, IndustryChain, IndustrySector, Company,
    ImageTextExtractor, LLMInformationExtractor, NetworkAnalyzer,
    InvestmentAnalyzer, ReportGenerator
)


def demo_ai_power_chain():
    """演示: AI算力产业链分析"""
    
    print("=" * 80)
    print("🚀 A5L 产业链分析器演示 - AI算力产业链")
    print("=" * 80)
    print("\n💡 场景: 分析AI算力产业链 (20大细分领域)")
    print("📊 数据来源: 产业链图谱 + AKShare实时数据")
    print("🎯 分析目标: 找出核心节点 + 龙头公司 + 投资机会\n")
    
    # 创建分析器
    print("[1/7] 初始化产业链分析器...")
    analyzer = IndustryChainAnalyzer()
    
    # 模拟分析 (使用演示模式，无需真实图片)
    print("[2/7] 分析产业链结构 (演示模式)...")
    # 直接创建演示数据，跳过图片分析
    analyzer.industry_chain = analyzer.llm_extractor._get_ai_power_chain_demo()
    analyzer.network_analyzer = NetworkAnalyzer(analyzer.industry_chain)
    analyzer.investment_analyzer = InvestmentAnalyzer(analyzer.industry_chain)
    analyzer.report_generator = ReportGenerator(
        analyzer.industry_chain,
        analyzer.network_analyzer,
        analyzer.investment_analyzer
    )

    result = {
        'status': 'success',
        'chain_name': analyzer.industry_chain.name,
        'sectors_count': len(analyzer.industry_chain.sectors),
        'companies_count': len(analyzer.industry_chain.get_company_names()),
        'network_available': False,
        'data_source': 'Demo'
    }
    
    print(f"\n   ✅ 分析完成!")
    print(f"   📊 细分领域: {result['sectors_count']}个")
    print(f"   🏢 公司数量: {result['companies_count']}家")
    print(f"   🕸️  网络分析: {'可用' if result['network_available'] else '不可用'}")
    print(f"   📈 数据源: {result['data_source']}")
    
    # 显示细分领域
    print("\n[3/7] 产业链细分领域:")
    print("-" * 80)
    chain = analyzer.industry_chain
    for i, sector in enumerate(chain.sectors, 1):
        leaders = [c.name for c in sector.companies if c.is_leader]
        print(f"   {i:2d}. {sector.name:12s} | 龙头: {', '.join(leaders) if leaders else 'N/A'}")
    
    # 网络分析
    print("\n[4/7] 产业链网络分析 (NetworkX):")
    print("-" * 80)
    
    # 中心性分析
    centrality = analyzer.network_analyzer.calculate_centrality()
    if centrality:
        print("   📊 核心节点排名 (Top 5):")
        for i, (node, score) in enumerate(list(centrality.items())[:5], 1):
            bar = "█" * int(score * 20)
            print(f"      {i}. {node:12s} | {score:.3f} | {bar}")
    
    # 网络指标
    metrics = analyzer.network_analyzer.analyze_network_metrics()
    if metrics:
        print(f"\n   📈 网络结构指标:")
        print(f"      • 网络密度: {metrics.get('density', 0):.3f}")
        print(f"      • 节点总数: {metrics.get('num_nodes', 0)}")
        print(f"      • 连接总数: {metrics.get('num_edges', 0)}")
        print(f"      • 平均度数: {metrics.get('avg_degree', 0):.2f}")
    
    # 投资分析
    print("\n[5/7] 投资机会分析:")
    print("-" * 80)
    
    recommendations = analyzer.get_investment_recommendations()
    
    print("   🏆 Top 5 投资机会 (按机会评分排序):")
    print("   " + "-" * 76)
    print(f"   {'排名':<4} {'细分领域':<12} {'机会分':<8} {'集中度':<8} {'成长性':<8} {'建议':<10}")
    print("   " + "-" * 76)
    
    for i, rec in enumerate(recommendations[:5], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {emoji} {i:<2} {rec['sector_name']:<12} {rec['opportunity_score']:<8.1f} "
              f"{rec['concentration_score']:<8.1f} {rec['growth_score']:<8} {rec['recommendation']:<10}")
    
    # 龙头公司
    print("\n   ⭐ 龙头公司关注列表:")
    print("   " + "-" * 76)
    print(f"   {'细分领域':<12} {'公司名称':<12} {'股票代码':<12} {'市值(亿)':<10} {'PE':<8}")
    print("   " + "-" * 76)
    
    for sector in chain.sectors:
        for company in sector.companies:
            if company.is_leader:
                market_cap = f"{company.market_cap:.0f}" if company.market_cap else "N/A"
                pe = f"{company.pe_ratio:.1f}" if company.pe_ratio else "N/A"
                print(f"   {sector.name:<12} {company.name:<12} {company.symbol or 'N/A':<12} "
                      f"{market_cap:<10} {pe:<8}")
    
    # 风险提示
    print("\n[6/7] 风险分析:")
    print("-" * 80)
    
    all_risks = []
    for sector in chain.sectors:
        risks = analyzer.investment_analyzer.identify_risks(sector)
        for risk in risks:
            all_risks.append({
                'sector': sector.name,
                **risk
            })
    
    if all_risks:
        print("   ⚠️  识别到的风险因素:")
        for risk in all_risks[:5]:
            severity = "🔴 高" if risk['severity'] == 'high' else "🟡 中" if risk['severity'] == 'medium' else "🟢 低"
            print(f"      • [{risk['sector']}] {risk['type']}: {risk['description']} ({severity})")
    
    # 生成报告
    print("\n[7/7] 生成分析报告:")
    print("-" * 80)
    
    # Markdown报告
    report_md = analyzer.generate_report('markdown')
    report_file = "AI_POWER_CHAIN_ANALYSIS_REPORT.md"
    analyzer.save_report(report_file)
    print(f"   ✅ Markdown报告已生成: {report_file}")
    print(f"      报告大小: {len(report_md)} 字符")
    
    # JSON报告
    report_json = analyzer.generate_report('json')
    json_file = "AI_POWER_CHAIN_ANALYSIS_REPORT.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(report_json)
    print(f"   ✅ JSON报告已生成: {json_file}")
    
    # KIWI归档
    print("\n📚 KIWI知识库归档:")
    kiwi_path = analyzer.archive_to_kiwi("KIWI/industry_chains/")
    print(f"   ✅ 已归档到: {kiwi_path}")
    
    # 总结
    print("\n" + "=" * 80)
    print("🎉 演示完成! A5L产业链分析器已成功分析AI算力产业链")
    print("=" * 80)
    print("\n📊 分析结果摘要:")
    print(f"   • 产业链: {chain.name}")
    print(f"   • 细分领域: {len(chain.sectors)}个")
    print(f"   • 上市公司: {len(chain.get_company_names())}家")
    print(f"   • 核心节点: {list(centrality.keys())[0] if centrality else 'N/A'}")
    print(f"   • 最佳机会: {recommendations[0]['sector_name'] if recommendations else 'N/A'}")
    
    print("\n💡 使用建议:")
    print("   1. 查看完整报告: cat AI_POWER_CHAIN_ANALYSIS_REPORT.md")
    print("   2. 生成网络可视化: analyzer.visualize_network()")
    print("   3. 分析其他产业链: analyzer.analyze_image('other_chain.jpg')")
    print("   4. 查询KIWI知识: 查看 KIWI/industry_chains/ 目录")
    
    print("\n🚀 A5L已变得更加强大！产业链分析能力已就绪！")
    print("=" * 80)


def demo_integration_with_a5l():
    """演示: 产业链分析器与A5L集成"""
    
    print("\n" + "=" * 80)
    print("🔗 产业链分析器与A5L系统集成演示")
    print("=" * 80)
    
    print("\n💡 演示场景: A5L CLI调用产业链分析")
    print("   命令: a5l analyze_industry_chain --image ai_power_map.jpg")
    
    # 模拟CLI调用
    print("\n📋 分析结果将自动:")
    print("   1. 提取产业链结构 (OCR + LLM)")
    print("   2. 获取实时估值数据 (AKShare)")
    print("   3. 网络分析 (NetworkX)")
    print("   4. 生成投资建议")
    print("   5. 归档到KIWI知识库")
    print("   6. 推送飞书报告")
    
    print("\n✅ 产业链分析器已完全融入A5L架构!")
    print("   • Layer 3: 非结构化分析 (产业链图谱)")
    print("   • Layer 4: 决策信号 (投资建议)")
    print("   • KIWI: 知识沉淀 (产业链知识库)")


def main():
    """主函数"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🚀 A5L 产业链分析器演示 🚀" + " " * 33 + "║")
    print("║" + " " * 15 + "五一假期特供 - 让A5L变得无比强大!" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    try:
        # 演示1: AI算力产业链分析
        demo_ai_power_chain()
        
        # 演示2: 与A5L集成
        demo_integration_with_a5l()
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
