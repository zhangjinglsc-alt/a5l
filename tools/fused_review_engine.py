#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fused Review Engine - 融合复盘系统
整合多种投资分析框架（浪主指数、巴菲特思维、因子投资等）
生成L1/L2/L3三层复盘报告
"""

import akshare as ak
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class FusedReviewEngine:
    """融合复盘引擎"""
    
    def __init__(self):
        self.data_dir = Path("/workspace/projects/workspace/data/review_layers")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def _get_market_data(self):
        """获取基础市场数据"""
        data = {
            "date": self.today,
            "timestamp": datetime.now().isoformat(),
            "indices": {},
            "sectors": [],
            "sentiment": {},
            "volume": {}
        }
        
        try:
            # 获取主要指数
            indices = {
                "000001": "上证指数",
                "399001": "深证成指", 
                "399006": "创业板指",
                "000688": "科创50"
            }
            
            for code, name in indices.items():
                try:
                    if code.startswith("000") or code.startswith("688"):
                        df = ak.index_zh_a_hist(symbol=code, period="daily", start_date=self.today.replace("-", ""), end_date=self.today.replace("-", ""))
                    else:
                        df = ak.index_zh_a_hist(symbol=code, period="daily", start_date=self.today.replace("-", ""), end_date=self.today.replace("-", ""))
                    
                    if not df.empty:
                        row = df.iloc[-1]
                        data["indices"][name] = {
                            "close": float(row.get("收盘", 0)),
                            "open": float(row.get("开盘", 0)),
                            "high": float(row.get("最高", 0)),
                            "low": float(row.get("最低", 0)),
                            "change_pct": float(row.get("涨跌幅", 0)),
                            "volume": float(row.get("成交量", 0)),
                            "amount": float(row.get("成交额", 0))
                        }
                except Exception as e:
                    print(f"获取{name}数据失败: {e}")
                    
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            
        # 获取涨跌家数
        try:
            zd = ak.stock_zt_pool_em(date=self.today.replace("-", ""))
            data["sentiment"]["limit_up_count"] = len(zd) if zd is not None else 0
        except:
            data["sentiment"]["limit_up_count"] = 0
            
        try:
            dt = ak.stock_zt_pool_dtgc_em(date=self.today.replace("-", ""))
            data["sentiment"]["limit_down_count"] = len(dt) if dt is not None else 0
        except:
            data["sentiment"]["limit_down_count"] = 0
            
        return data
    
    def _apply_langzhu_analysis(self, data):
        """浪主指数分析 - 波浪理论"""
        analysis = {
            "framework": "浪主指数",
            "wave_position": "未知",
            "key_levels": {},
            "direction": "观望",
            "confidence": 0.5
        }
        
        sh = data.get("indices", {}).get("上证指数", {})
        change = sh.get("change_pct", 0)
        
        # 简化浪型判断
        if change > 1.5:
            analysis["wave_position"] = "主升浪/反弹浪"
            analysis["direction"] = "看多"
            analysis["confidence"] = 0.7
        elif change > 0.5:
            analysis["wave_position"] = "上涨中继"
            analysis["direction"] = "偏多"
            analysis["confidence"] = 0.6
        elif change < -1.5:
            analysis["wave_position"] = "主跌浪/调整浪"
            analysis["direction"] = "看空"
            analysis["confidence"] = 0.7
        elif change < -0.5:
            analysis["wave_position"] = "下跌中继"
            analysis["direction"] = "偏空"
            analysis["confidence"] = 0.6
        else:
            analysis["wave_position"] = "震荡整理"
            analysis["direction"] = "观望"
            analysis["confidence"] = 0.5
            
        analysis["key_levels"] = {
            "support": sh.get("low", 0),
            "resistance": sh.get("high", 0),
            "current": sh.get("close", 0)
        }
        
        return analysis
    
    def _apply_buffett_analysis(self, data):
        """巴菲特价值投资思维 - 市场情绪分析"""
        analysis = {
            "framework": "巴菲特情绪",
            "stage": "未知",
            "divergence": "medium",
            "contrarian_opportunity": False,
            "sentiment_score": 50
        }
        
        sentiment = data.get("sentiment", {})
        up_count = sentiment.get("limit_up_count", 0)
        down_count = sentiment.get("limit_down_count", 0)
        
        # 计算情绪得分
        if up_count + down_count > 0:
            sentiment_score = (up_count / (up_count + down_count)) * 100
        else:
            sentiment_score = 50
            
        analysis["sentiment_score"] = sentiment_score
        
        # 三阶段判断
        if sentiment_score > 80:
            analysis["stage"] = "情绪阶段（高潮）"
            analysis["divergence"] = "high"
            analysis["contrarian_opportunity"] = False  # 等回调
        elif sentiment_score > 60:
            analysis["stage"] = "预期阶段（乐观）"
            analysis["divergence"] = "medium"
        elif sentiment_score > 40:
            analysis["stage"] = "现实阶段（分歧）"
            analysis["divergence"] = "low"
            analysis["contrarian_opportunity"] = True
        elif sentiment_score > 20:
            analysis["stage"] = "情绪阶段（恐慌）"
            analysis["divergence"] = "medium"
            analysis["contrarian_opportunity"] = True
        else:
            analysis["stage"] = "情绪阶段（冰点）"
            analysis["divergence"] = "high"
            analysis["contrarian_opportunity"] = True
            
        return analysis
    
    def _apply_factor_analysis(self, data):
        """因子投资方法论 - 风格分析"""
        analysis = {
            "framework": "因子投资",
            "dominant_style": "均衡",
            "active_factors": [],
            "factor_scores": {}
        }
        
        indices = data.get("indices", {})
        
        # 风格判断
        cyb = indices.get("创业板指", {}).get("change_pct", 0)
        sh = indices.get("上证指数", {}).get("change_pct", 0)
        kc = indices.get("科创50", {}).get("change_pct", 0)
        
        # 成长vs价值判断
        if cyb > sh + 0.5:
            analysis["dominant_style"] = "成长风格占优"
            analysis["active_factors"].append("成长因子")
        elif sh > cyb + 0.5:
            analysis["dominant_style"] = "价值风格占优"
            analysis["active_factors"].append("价值因子")
        else:
            analysis["dominant_style"] = "均衡风格"
            
        # 大小盘判断
        if kc > sh:
            analysis["active_factors"].append("小盘因子")
        else:
            analysis["active_factors"].append("大盘因子")
            
        # 动量判断
        if sh > 0:
            analysis["active_factors"].append("动量因子")
        else:
            analysis["active_factors"].append("反转因子")
            
        analysis["factor_scores"] = {
            "growth": cyb,
            "value": sh,
            "tech": kc
        }
        
        return analysis
    
    def generate_layer1_basic(self, force_refresh=False):
        """
        L1基础层 - 收集原始市场数据
        """
        output_file = self.data_dir / f"layer1_basic_{self.today}.json"
        
        # 检查缓存
        if output_file.exists() and not force_refresh:
            print(f"L1基础层已存在: {output_file}")
            return str(output_file)
            
        print("📊 正在生成L1基础层数据...")
        
        # 获取基础数据
        data = self._get_market_data()
        
        # 保存L1数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ L1基础层生成完成: {output_file}")
        return str(output_file)
    
    def generate_layer2_deep(self, force_refresh=False):
        """
        L2深度层 - 应用多框架分析
        """
        output_file = self.data_dir / f"layer2_deep_{self.today}.json"
        
        # 检查缓存
        if output_file.exists() and not force_refresh:
            print(f"L2深度层已存在: {output_file}")
            return str(output_file)
            
        # 先确保L1存在
        l1_file = self.data_dir / f"layer1_basic_{self.today}.json"
        if not l1_file.exists():
            self.generate_layer1_basic()
            
        # 加载L1数据
        with open(l1_file, 'r', encoding='utf-8') as f:
            l1_data = json.load(f)
            
        print("🔍 正在生成L2深度层分析...")
        
        # 应用多框架分析
        analysis = {
            "date": self.today,
            "timestamp": datetime.now().isoformat(),
            "frameworks": {}
        }
        
        # 浪主指数分析
        analysis["frameworks"]["langzhu"] = self._apply_langzhu_analysis(l1_data)
        
        # 巴菲特情绪分析
        analysis["frameworks"]["buffett"] = self._apply_buffett_analysis(l1_data)
        
        # 因子投资分析
        analysis["frameworks"]["factor"] = self._apply_factor_analysis(l1_data)
        
        # 保存L2数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        print(f"✅ L2深度层生成完成: {output_file}")
        return str(output_file)
    
    def generate_layer3_comprehensive(self, force_refresh=False):
        """
        L3综合层 - 融合各框架生成最终复盘报告
        """
        output_file = self.data_dir / f"layer3_comprehensive_{self.today}.json"
        report_file = self.data_dir / f"layer3_report_{self.today}.md"
        
        # 检查缓存
        if output_file.exists() and not force_refresh:
            print(f"L3综合层已存在: {output_file}")
            return str(output_file)
            
        # 先确保L2存在
        l2_file = self.data_dir / f"layer2_deep_{self.today}.json"
        if not l2_file.exists():
            self.generate_layer2_deep()
            
        # 加载L2数据
        with open(l2_file, 'r', encoding='utf-8') as f:
            l2_data = json.load(f)
            
        print("🧠 正在生成L3综合层报告...")
        
        # 融合分析
        frameworks = l2_data.get("frameworks", {})
        
        # 综合判断
        langzhu = frameworks.get("langzhu", {})
        buffett = frameworks.get("buffett", {})
        factor = frameworks.get("factor", {})
        
        # 方向一致性检查
        directions = [
            langzhu.get("direction", "观望"),
            "看多" if buffett.get("contrarian_opportunity") and buffett.get("sentiment_score", 50) < 30 else "观望",
            factor.get("dominant_style", "均衡")
        ]
        
        # 生成综合结论
        consensus = {
            "date": self.today,
            "timestamp": datetime.now().isoformat(),
            "summary": self._generate_summary(frameworks),
            "predictions": {
                "langzhu": {
                    "direction": langzhu.get("direction", "观望"),
                    "confidence": langzhu.get("confidence", 0.5)
                },
                "buffett": {
                    "divergence": buffett.get("divergence", "medium"),
                    "contrarian": buffett.get("contrarian_opportunity", False)
                },
                "factor": {
                    "style": factor.get("dominant_style", "均衡"),
                    "factors": factor.get("active_factors", [])
                }
            },
            "recommendations": self._generate_recommendations(frameworks),
            "frameworks": frameworks
        }
        
        # 保存L3 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consensus, f, indent=2, ensure_ascii=False)
            
        # 生成Markdown报告
        report = self._generate_markdown_report(consensus)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"✅ L3综合层生成完成: {output_file}")
        print(f"📄 复盘报告: {report_file}")
        return str(output_file)
    
    def _generate_summary(self, frameworks):
        """生成综合摘要"""
        langzhu = frameworks.get("langzhu", {})
        buffett = frameworks.get("buffett", {})
        factor = frameworks.get("factor", {})
        
        summary = f"""
## 融合复盘摘要 ({self.today})

### 浪主指数视角
- 当前位置: {langzhu.get('wave_position', '未知')}
- 方向判断: {langzhu.get('direction', '观望')}
- 关键点位: 支撑{langzhu.get('key_levels', {}).get('support', 'N/A')} / 压力{langzhu.get('key_levels', {}).get('resistance', 'N/A')}

### 巴菲特情绪视角  
- 市场阶段: {buffett.get('stage', '未知')}
- 情绪得分: {buffett.get('sentiment_score', 50):.0f}/100
- 逆向机会: {'✅ 是' if buffett.get('contrarian_opportunity') else '❌ 否'}

### 因子投资视角
- 主导风格: {factor.get('dominant_style', '均衡')}
- 活跃因子: {', '.join(factor.get('active_factors', []))}

### 融合结论
综合三个框架分析，当前市场处于**{langzhu.get('wave_position', '震荡')}**，
情绪**{buffett.get('stage', '中性')}**，风格偏向**{factor.get('dominant_style', '均衡')}**。
        """
        return summary.strip()
    
    def _generate_recommendations(self, frameworks):
        """生成操作建议"""
        langzhu = frameworks.get("langzhu", {})
        buffett = frameworks.get("buffett", {})
        
        recommendations = []
        
        # 基于浪主判断
        if langzhu.get("direction") in ["看多", "偏多"]:
            recommendations.append("浪主框架建议: 保持仓位，关注反弹持续性")
        elif langzhu.get("direction") in ["看空", "偏空"]:
            recommendations.append("浪主框架建议: 控制仓位，等待企稳信号")
        else:
            recommendations.append("浪主框架建议: 观望为主，等待方向明确")
            
        # 基于巴菲特判断
        if buffett.get("contrarian_opportunity") and buffett.get("sentiment_score", 50) < 30:
            recommendations.append("巴菲特框架建议: 情绪冰点，关注逆向买入机会")
        elif buffett.get("sentiment_score", 50) > 80:
            recommendations.append("巴菲特框架建议: 情绪过热，警惕回调风险")
        else:
            recommendations.append("巴菲特框架建议: 情绪中性，按基本面操作")
            
        return recommendations
    
    def _generate_markdown_report(self, consensus):
        """生成Markdown格式复盘报告"""
        report = f"""# 📊 融合复盘系统 - L3综合层报告

**报告日期**: {self.today}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{consensus.get('summary', '')}

---

## 🎯 各框架预测

### 浪主指数
- **方向**: {consensus.get('predictions', {}).get('langzhu', {}).get('direction', '观望')}
- **置信度**: {consensus.get('predictions', {}).get('langzhu', {}).get('confidence', 0.5):.0%}

### 巴菲特情绪
- **分歧度**: {consensus.get('predictions', {}).get('buffett', {}).get('divergence', 'medium')}
- **逆向机会**: {'是' if consensus.get('predictions', {}).get('buffett', {}).get('contrarian') else '否'}

### 因子投资
- **风格**: {consensus.get('predictions', {}).get('factor', {}).get('style', '均衡')}
- **活跃因子**: {', '.join(consensus.get('predictions', {}).get('factor', {}).get('factors', []))}

---

## 💡 操作建议

"""
        for i, rec in enumerate(consensus.get('recommendations', []), 1):
            report += f"{i}. {rec}\n"
            
        report += f"""

---

## 🧬 进化记录

- **数据来源**: 融合复盘系统 v1.0
- **分析框架**: 浪主指数 + 巴菲特情绪 + 因子投资
- **保存路径**: {self.data_dir}

---

*报告由融合复盘系统自动生成，仅供参考*
"""
        return report


def main():
    """主函数 - 测试用"""
    engine = FusedReviewEngine()
    
    print("=" * 60)
    print("融合复盘系统 - 全层生成测试")
    print("=" * 60)
    
    # 生成L1
    l1_result = engine.generate_layer1_basic(force_refresh=True)
    print(f"\nL1结果: {l1_result}")
    
    # 生成L2
    l2_result = engine.generate_layer2_deep(force_refresh=True)
    print(f"\nL2结果: {l2_result}")
    
    # 生成L3
    l3_result = engine.generate_layer3_comprehensive(force_refresh=True)
    print(f"\nL3结果: {l3_result}")
    
    print("\n" + "=" * 60)
    print("融合复盘系统 - 生成完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
