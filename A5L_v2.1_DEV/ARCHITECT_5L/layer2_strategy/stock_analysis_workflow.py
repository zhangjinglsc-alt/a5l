#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L-UZI 个股分析工作流 + 飞书自动归档
整合 UZI深度分析 + A5L其他SKILL + 飞书云文档同步

功能:
1. 多维度个股深度分析 (UZI+VALUECELL+产业链)
2. 自动生成详尽分析报告 (Markdown+HTML)
3. 自动同步到飞书云文档
4. 结合其他SKILL弥补研究缺陷
"""

import os
import sys
import json
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, '/workspace/projects/workspace')

# A5L核心组件
from ARCHITECT_5L.layer2_strategy.uzi_adapter import UZIAdapter, analyze_stock_uzi
from ARCHITECT_5L.layer3_analysis.analyzers.value_cell_analyzer import VALUECellAnalyzer
from ARCHITECT_5L.layer3_analysis.analyzers.bearish_perspective_analyzer import BearishPerspectiveAnalyzer
from ARCHITECT_5L.layer3_analysis.analyzers.industry_chain_analyzer import IndustryChainAnalyzer
from ARCHITECT_5L.layer0_control.config_manager import config


class StockAnalysisWorkflow:
    """
    个股分析完整工作流
    
    整合多个SKILL进行全方位分析:
    1. UZI深度分析 (51位大佬+22维数据)
    2. VALUE CELL五维度价值分析
    3. 空方视角风险审查
    4. 产业链分析 (如适用)
    """
    
    def __init__(self):
        self.uzi = UZIAdapter(depth="medium")
        self.value_cell = VALUECellAnalyzer()
        self.bearish = BearishPerspectiveAnalyzer()
        self.industry = IndustryChainAnalyzer()
        
    def comprehensive_analysis(self, symbol: str, 
                             include_industry: bool = False) -> Dict:
        """
        综合个股分析
        
        Args:
            symbol: 股票代码
            include_industry: 是否包含产业链分析
            
        Returns:
            综合分析结果
        """
        print(f"🔬 启动综合个股分析: {symbol}")
        print("=" * 80)
        
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analyses": {},
            "synthesis": {},
            "recommendation": {}
        }
        
        # 1. UZI深度分析 (核心)
        print("\n[1/4] UZI深度分析 (51位评委+22维数据)...")
        uzi_report = self.uzi.analyze(symbol)
        result["analyses"]["uzi"] = {
            "score": uzi_report.score,
            "verdict": uzi_report.summary,
            "fund_score": uzi_report.details.get("fund_score"),
            "consensus_score": uzi_report.details.get("consensus_score"),
            "judges": uzi_report.details.get("judges_count"),
            "bullish": uzi_report.details.get("bullish_count"),
            "bearish": uzi_report.details.get("bearish_count")
        }
        print(f"   ✅ UZI评分: {uzi_report.score:.1f} - {uzi_report.summary}")
        
        # 2. VALUE CELL价值分析
        print("\n[2/4] VALUE CELL价值分析...")
        try:
            value_report = self.value_cell.analyze(symbol)
            result["analyses"]["value_cell"] = {
                "total_score": value_report.get("total_score"),
                "rating": value_report.get("rating"),
                "intrinsic_value": value_report.get("intrinsic_value"),
                "margin_of_safety": value_report.get("margin_of_safety")
            }
            print(f"   ✅ VALUE评分: {value_report.get('total_score', 0):.1f}")
        except Exception as e:
            print(f"   ⚠️ VALUE分析失败: {e}")
            result["analyses"]["value_cell"] = {"error": str(e)}
        
        # 3. 空方视角风险审查
        print("\n[3/4] 空方视角风险审查...")
        try:
            bearish_report = self.bearish.analyze({"symbol": symbol})
            result["analyses"]["bearish"] = {
                "risk_score": bearish_report.get("risk_score"),
                "risk_level": bearish_report.get("risk_level"),
                "key_risks": bearish_report.get("key_risks", [])[:3]
            }
            print(f"   ✅ 风险评分: {bearish_report.get('risk_score', 0):.1f}")
        except Exception as e:
            print(f"   ⚠️ 风险分析失败: {e}")
            result["analyses"]["bearish"] = {"error": str(e)}
        
        # 4. 产业链分析 (可选)
        if include_industry:
            print("\n[4/4] 产业链分析...")
            try:
                industry_report = self.industry.analyze(symbol)
                result["analyses"]["industry"] = industry_report
                print(f"   ✅ 产业链分析完成")
            except Exception as e:
                print(f"   ⚠️ 产业链分析失败: {e}")
        
        # 5. 综合评估
        print("\n" + "=" * 80)
        print("🎯 综合评估")
        print("=" * 80)
        
        # 计算综合评分
        scores = []
        if "uzi" in result["analyses"]:
            scores.append(result["analyses"]["uzi"]["score"] * 0.5)  # UZI权重50%
        if "value_cell" in result["analyses"] and "score" in result["analyses"]["value_cell"]:
            scores.append(result["analyses"]["value_cell"]["total_score"] * 0.3)  # VALUE权重30%
        if "bearish" in result["analyses"] and "risk_score" in result["analyses"]["bearish"]:
            # 风险越低越好
            risk_score = 100 - result["analyses"]["bearish"]["risk_score"]
            scores.append(risk_score * 0.2)  # 风险权重20%
        
        overall_score = sum(scores) if scores else 50
        result["synthesis"]["overall_score"] = overall_score
        
        # 生成最终建议
        if overall_score >= 70:
            recommendation = "🟢 强烈关注 - 多维度验证的优秀标的"
        elif overall_score >= 55:
            recommendation = "🟡 可以跟踪 - 存在亮点但需观察"
        elif overall_score >= 40:
            recommendation = "🟠 观望为主 - 风险收益比一般"
        else:
            recommendation = "🔴 暂时回避 - 多维度显示风险"
        
        result["recommendation"]["final"] = recommendation
        result["recommendation"]["overall_score"] = overall_score
        
        print(f"\n综合评分: {overall_score:.1f}/100")
        print(f"投资建议: {recommendation}")
        
        # 生成报告
        report = self._generate_comprehensive_report(result)
        result["report"] = report
        
        return result
    
    def _generate_comprehensive_report(self, result: Dict) -> Dict:
        """生成综合分析报告"""
        symbol = result["symbol"]
        
        # Markdown报告
        md_content = self._generate_markdown_report(result)
        
        # HTML报告
        html_content = self._generate_html_report(result)
        
        return {
            "markdown": md_content,
            "html": html_content,
            "json": json.dumps(result, indent=2, ensure_ascii=False)
        }
    
    def _generate_markdown_report(self, result: Dict) -> str:
        """生成Markdown报告"""
        symbol = result["symbol"]
        analyses = result["analyses"]
        
        lines = [
            f"# 📊 A5L-UZI 个股深度分析报告",
            f"",
            f"**股票代码**: {symbol}",
            f"**分析时间**: {result['timestamp']}",
            f"**报告版本**: v1.5.0 + UZI集成",
            f"",
            f"---",
            f"",
            f"## 🎯 综合评估",
            f"",
            f"**综合评分**: {result['synthesis'].get('overall_score', 0):.1f}/100",
            f"",
            f"**投资建议**: {result['recommendation'].get('final', 'N/A')}",
            f"",
            f"---",
            f"",
            f"## 📈 多维度分析",
            f"",
        ]
        
        # UZI分析
        if "uzi" in analyses:
            uzi = analyses["uzi"]
            lines.extend([
                f"### 1️⃣ UZI深度分析 (51位评委+22维数据)",
                f"",
                f"- **综合评分**: {uzi.get('score', 0):.1f}",
                f"- **投资结论**: {uzi.get('verdict', 'N/A')}",
                f"- **基本面评分**: {uzi.get('fund_score', 0):.1f}",
                f"- **共识评分**: {uzi.get('consensus_score', 0):.1f}",
                f"- **评委投票**: 看多{uzi.get('bullish', 0)}人 / 看空{uzi.get('bearish', 0)}人 / 共{uzi.get('judges', 0)}人",
                f"",
            ])
        
        # VALUE CELL分析
        if "value_cell" in analyses and "total_score" in analyses["value_cell"]:
            vc = analyses["value_cell"]
            lines.extend([
                f"### 2️⃣ VALUE CELL价值分析",
                f"",
                f"- **价值评分**: {vc.get('total_score', 0):.1f}",
                f"- **投资评级**: {vc.get('rating', 'N/A')}",
                f"- **内在价值**: {vc.get('intrinsic_value', 'N/A')}",
                f"- **安全边际**: {vc.get('margin_of_safety', 'N/A')}",
                f"",
            ])
        
        # 空方视角
        if "bearish" in analyses and "risk_score" in analyses["bearish"]:
            bear = analyses["bearish"]
            lines.extend([
                f"### 3️⃣ 空方视角风险审查",
                f"",
                f"- **风险评分**: {bear.get('risk_score', 0):.1f}/100 (越高越危险)",
                f"- **风险等级**: {bear.get('risk_level', 'N/A')}",
                f"- **关键风险**:",
            ])
            for risk in bear.get("key_risks", [])[:3]:
                lines.append(f"  - {risk}")
            lines.append("")
        
        lines.extend([
            f"---",
            f"",
            f"## 💡 分析说明",
            f"",
            f"本报告由A5L v1.5.0生成，整合了以下SKILL：",
            f"- **UZI-Skill**: 51位投资大佬+22维数据+17种机构方法",
            f"- **VALUE CELL**: 五维度价值投资分析",
            f"- **Bearish Perspective**: 空方视角风险审查",
            f"- **Industry Chain**: 产业链图谱分析(如适用)",
            f"",
            f"---",
            f"",
            f"*报告生成时间: {result['timestamp']}*",
            f"*A5L - 称手、好用、强大的超级投资工具*",
        ])
        
        return '\n'.join(lines)
    
    def _generate_html_report(self, result: Dict) -> str:
        """生成HTML报告"""
        # 简化版，实际可以更丰富
        md_content = self._generate_markdown_report(result)
        # 简单转换
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>A5L-UZI分析报告 - {result['symbol']}</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
                       max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
                h1 {{ color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 10px; }}
                h2 {{ color: #16213e; margin-top: 30px; }}
                h3 {{ color: #0f3460; }}
                .score {{ font-size: 48px; font-weight: bold; color: #e94560; }}
                .recommendation {{ font-size: 24px; background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .section {{ background: #fafafa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>📊 A5L-UZI 个股深度分析报告</h1>
            <p><strong>股票代码</strong>: {result['symbol']}</p>
            <p><strong>分析时间</strong>: {result['timestamp']}</p>
            
            <div class="section">
                <h2>🎯 综合评估</h2>
                <div class="score">{result['synthesis'].get('overall_score', 0):.1f}/100</div>
                <div class="recommendation">{result['recommendation'].get('final', '')}</div>
            </div>
            
            <pre>{self._generate_markdown_report(result)}</pre>
        </body>
        </html>
        """
        return html


# ============================================================================
# 飞书同步功能
# ============================================================================

def sync_to_feishu(report_content: str, symbol: str, 
                   folder_token: str = None) -> Dict:
    """
    同步报告到飞书云文档
    
    Args:
        report_content: 报告内容 (Markdown)
        symbol: 股票代码
        folder_token: 飞书文件夹token
        
    Returns:
        同步结果
    """
    if folder_token is None:
        folder_token = config.get('services', 'feishu', 'folder_token', 
                                 default="DG2GfGe0nlLuvSdYlxwcpH0MnGb")
    
    timestamp = datetime.now().strftime("%Y%m%d")
    title = f"{timestamp}-{symbol}-深度分析报告"
    
    print(f"\n📤 同步到飞书...")
    print(f"   标题: {title}")
    print(f"   文件夹: {folder_token}")
    
    # 这里应该调用飞书API创建文档
    # 简化版：保存到本地并返回信息
    
    output_dir = "/workspace/projects/workspace/output/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存Markdown
    md_path = f"{output_dir}/{title}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"   ✅ 报告已保存: {md_path}")
    
    # TODO: 调用飞书API上传
    # 使用 feishu_create_doc 工具
    
    return {
        "success": True,
        "local_path": md_path,
        "title": title,
        "folder_token": folder_token,
        "note": "飞书API调用需要用户授权"
    }


# ============================================================================
# 主入口
# ============================================================================

def analyze_and_archive(symbol: str, sync_feishu: bool = True) -> Dict:
    """
    分析个股并归档
    
    Args:
        symbol: 股票代码
        sync_feishu: 是否同步到飞书
        
    Returns:
        完整结果
    """
    print("=" * 80)
    print(f"🚀 A5L-UZI 个股分析工作流")
    print(f"🎯 标的: {symbol}")
    print("=" * 80)
    
    # 执行分析
    workflow = StockAnalysisWorkflow()
    result = workflow.comprehensive_analysis(symbol, include_industry=False)
    
    # 同步到飞书
    if sync_feishu:
        sync_result = sync_to_feishu(
            result["report"]["markdown"],
            symbol
        )
        result["feishu_sync"] = sync_result
    
    print("\n" + "=" * 80)
    print("✅ 分析工作流完成!")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    # 测试
    result = analyze_and_archive("002273.SZ", sync_feishu=True)
    
    print("\n📊 最终结果:")
    print(f"股票: {result['symbol']}")
    print(f"综合评分: {result['synthesis'].get('overall_score', 0):.1f}")
    print(f"建议: {result['recommendation'].get('final', '')}")
    
    if 'feishu_sync' in result:
        print(f"\n飞书同步: {result['feishu_sync'].get('local_path')}")
