#!/usr/bin/env python3
"""
Operation DATA AWAKENING - Phase 4: 交易策略形成
构建跨SKILL策略组合矩阵和详细交易规则
"""

import json
from datetime import datetime
from typing import Dict, List

class StrategyMatrixBuilder:
    """策略矩阵构建器"""
    
    def __init__(self):
        self.matrix = {}
        self.rules = {}
        
    def build_strategy_matrix(self) -> Dict:
        """构建策略矩阵"""
        print("  📊 构建策略矩阵...")
        
        matrix = {
            "矩阵定义": {
                "维度1": "策略类型 (趋势/均值回归/突破/价值)",
                "维度2": "适用市场 (A股/美股/港股)",
                "维度3": "风险等级 (低/中/高)",
                "维度4": "主导SKILL"
            },
            "策略列表": [
                {
                    "id": "STRAT_001",
                    "name": "超短打板策略",
                    "主导SKILL": ["yangguan-daodao", "technical-analysis"],
                    "适用市场": ["A股"],
                    "风险等级": "高",
                    "策略逻辑": "涨停板突破+量价齐升",
                    "入场条件": [
                        "首板或二连板",
                        "换手率>5%",
                        "封单金额>1亿",
                        "板块热度前3"
                    ],
                    "出场条件": [
                        "开板且5分钟内未回封",
                        "次日低开-3%",
                        "达到止盈点+10%"
                    ],
                    "仓位": 0.1,
                    "最大持仓": 3
                },
                {
                    "id": "STRAT_002",
                    "name": "趋势跟踪策略",
                    "主导SKILL": ["technical-analysis", "sector-etf-monitor"],
                    "适用市场": ["A股", "美股", "港股"],
                    "风险等级": "中",
                    "策略逻辑": "20日均线突破+板块确认",
                    "入场条件": [
                        "股价突破20日均线",
                        "成交量>20日均量1.5倍",
                        "板块RS>1.2",
                        "大盘趋势向上"
                    ],
                    "出场条件": [
                        "股价跌破20日均线",
                        "板块RS<0.8",
                        "达到止损点-8%"
                    ],
                    "仓位": 0.2,
                    "最大持仓": 5
                },
                {
                    "id": "STRAT_003",
                    "name": "价值投资策略",
                    "主导SKILL": ["buffett-value-investing", "stock-five-steps"],
                    "适用市场": ["A股", "美股", "港股"],
                    "风险等级": "低",
                    "策略逻辑": "低估值+高质量+合理价格",
                    "入场条件": [
                        "PE<行业均值80%",
                        "ROE>15%持续3年",
                        "股息率>3%",
                        "股价<内在价值80%"
                    ],
                    "出场条件": [
                        "PE>行业均值120%",
                        "ROE<10%",
                        "股价>内在价值120%",
                        "基本面恶化"
                    ],
                    "仓位": 0.25,
                    "最大持仓": 8
                },
                {
                    "id": "STRAT_004",
                    "name": "因子轮动策略",
                    "主导SKILL": ["factor-investing", "quant_analysis"],
                    "适用市场": ["A股"],
                    "风险等级": "中",
                    "策略逻辑": "多因子评分+月度轮动",
                    "入场条件": [
                        "综合因子评分前10%",
                        "动量因子>70分位",
                        "质量因子>60分位",
                        "估值因子<40分位"
                    ],
                    "出场条件": [
                        "因子评分掉出前30%",
                        "月度轮动信号",
                        "因子有效性衰减"
                    ],
                    "仓位": 0.15,
                    "最大持仓": 10
                },
                {
                    "id": "STRAT_005",
                    "name": "事件驱动策略",
                    "主导SKILL": ["catalyst-monitor-auto", "ai-llm"],
                    "适用市场": ["A股", "美股"],
                    "风险等级": "高",
                    "策略逻辑": "催化剂识别+预期差交易",
                    "入场条件": [
                        "Tier 1/2催化事件",
                        "市场情绪<70分",
                        "相关度>0.8",
                        "启动初期"
                    ],
                    "出场条件": [
                        "催化兑现",
                        "一致性高潮>90分",
                        "事件落地",
                        "达到止损-10%"
                    ],
                    "仓位": 0.1,
                    "最大持仓": 3
                },
                {
                    "id": "STRAT_006",
                    "name": "对冲套利策略",
                    "主导SKILL": ["quant_analysis", "fx-factor-monitor"],
                    "适用市场": ["港股", "美股"],
                    "风险等级": "低",
                    "策略逻辑": "统计套利+风险对冲",
                    "入场条件": [
                        "价差偏离均值2σ",
                        "相关性>0.9",
                        "波动率适中",
                        "无重大事件"
                    ],
                    "出场条件": [
                        "价差回归均值",
                        "相关性破裂<0.7",
                        "达到目标收益5%"
                    ],
                    "仓位": 0.2,
                    "最大持仓": 4
                }
            ]
        }
        
        self.matrix = matrix
        return matrix
    
    def build_risk_management_rules(self) -> Dict:
        """构建风险管理规则"""
        print("  🛡️ 构建风险管理规则...")
        
        rules = {
            "账户级别风控": {
                "最大总仓位": 0.8,
                "现金储备": 0.2,
                "单日最大亏损": 0.05,
                "最大回撤": 0.15,
                "止损线": 0.2
            },
            "策略级别风控": {
                "策略仓位上限": {
                    "低风险策略": 0.25,
                    "中风险策略": 0.2,
                    "高风险策略": 0.1
                },
                "策略持仓上限": {
                    "低风险策略": 10,
                    "中风险策略": 5,
                    "高风险策略": 3
                }
            },
            "个股级别风控": {
                "单只股票仓位上限": 0.1,
                "止损比例": 0.08,
                "止盈比例": 0.15,
                "追踪止损": True,
                "最大持有天数": 60
            },
            "板块级别风控": {
                "单一板块暴露上限": 0.3,
                "相关板块集中度上限": 0.5,
                "板块轮动监控": "weekly"
            },
            "熔断机制": {
                "日内熔断": {
                    "-5%": "暂停开新仓",
                    "-7%": "减仓50%",
                    "-10%": "清仓观望"
                },
                "连续亏损熔断": {
                    "3日连亏": "减仓至50%",
                    "5日连亏": "减仓至30%",
                    "7日连亏": "暂停交易，复盘"
                }
            }
        }
        
        self.rules = rules
        return rules
    
    def build_portfolio_allocation(self) -> Dict:
        """构建组合配置"""
        print("  ⚖️ 构建组合配置...")
        
        return {
            "配置目标": {
                "预期年化收益": "15-25%",
                "最大回撤": "<15%",
                "夏普比率": ">1.2",
                "胜率": ">55%"
            },
            "策略权重": {
                "价值投资策略": 0.25,
                "趋势跟踪策略": 0.20,
                "因子轮动策略": 0.15,
                "对冲套利策略": 0.20,
                "超短打板策略": 0.10,
                "事件驱动策略": 0.10
            },
            "动态调整": {
                "调整频率": "月度",
                "调整依据": [
                    "市场环境评分",
                    "策略有效性追踪",
                    "风险偏好变化"
                ],
                "调整规则": "±10%范围内微调"
            }
        }
    
    def generate_report(self) -> str:
        """生成Phase 4报告"""
        report = f"""# Operation DATA AWAKENING - Phase 4 Report
**执行时间**: {datetime.now().isoformat()}
**阶段**: 交易策略形成

## 策略矩阵

### 策略概览

| ID | 策略名称 | 主导SKILL | 适用市场 | 风险等级 | 仓位 |
|:---|:---------|:----------|:---------|:---------|:-----|
"""
        
        for strategy in self.matrix.get('策略列表', []):
            skills_str = ', '.join(strategy['主导SKILL'][:2])
            markets_str = '/'.join(strategy['适用市场'])
            report += f"| {strategy['id']} | {strategy['name']} | {skills_str} | {markets_str} | {strategy['风险等级']} | {strategy['仓位']*100:.0f}% |\n"
        
        report += f"""
## 策略详情

"""
        
        for strategy in self.matrix.get('策略列表', []):
            report += f"""### {strategy['name']} ({strategy['id']})

**策略逻辑**: {strategy['策略逻辑']}

**入场条件**:
"""
            for condition in strategy['入场条件']:
                report += f"- {condition}\n"
            
            report += f"\n**出场条件**:\n"
            for condition in strategy['出场条件']:
                report += f"- {condition}\n"
            
            report += f"""\n**风控参数**:
- 仓位上限: {strategy['仓位']*100:.0f}%
- 最大持仓: {strategy['最大持仓']}只

---

"""
        
        report += f"""## 风险管理规则

### 账户级别
- **最大总仓位**: {self.rules['账户级别风控']['最大总仓位']*100:.0f}%
- **现金储备**: {self.rules['账户级别风控']['现金储备']*100:.0f}%
- **单日最大亏损**: {self.rules['账户级别风控']['单日最大亏损']*100:.0f}%
- **最大回撤**: {self.rules['账户级别风控']['最大回撤']*100:.0f}%

### 熔断机制
- **-5%**: 暂停开新仓
- **-7%**: 减仓50%
- **-10%**: 清仓观望

## 下一步

1. 部署策略到模拟交易系统
2. 开始实盘回测
3. 监控策略有效性
4. 持续优化参数

---
**Phase 4完成时间**: {datetime.now().isoformat()}
**下一步**: Phase 5 - SKILL超级迭代
"""
        return report

def main():
    """Phase 4 主程序"""
    print("=" * 70)
    print("OPERATION DATA AWAKENING - Phase 4")
    print("交易策略形成")
    print("=" * 70)
    
    builder = StrategyMatrixBuilder()
    
    # 构建策略矩阵
    matrix = builder.build_strategy_matrix()
    
    # 构建风控规则
    rules = builder.build_risk_management_rules()
    
    # 构建组合配置
    allocation = builder.build_portfolio_allocation()
    
    # 生成报告
    report = builder.generate_report()
    
    # 保存配置
    output = {
        "timestamp": datetime.now().isoformat(),
        "strategy_matrix": matrix,
        "risk_rules": rules,
        "portfolio_allocation": allocation
    }
    
    with open('/workspace/projects/workspace/reports/phase4_strategy_matrix.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    with open('/workspace/projects/workspace/reports/phase4_strategy_matrix.md', 'w') as f:
        f.write(report)
    
    # 保存策略配置
    with open('/workspace/projects/workspace/systems/strategy_matrix_v1.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("📊 Phase 4 总结")
    print("=" * 70)
    print(f"✅ 策略矩阵构建完成")
    print(f"📄 策略配置: systems/strategy_matrix_v1.json")
    print(f"📄 详细报告: reports/phase4_strategy_matrix.md")
    print(f"\n🎯 策略组合:")
    print(f"  - 策略数量: {len(matrix['策略列表'])} 个")
    print(f"  - 风险覆盖: 低/中/高三档")
    print(f"  - 市场覆盖: A股/美股/港股")
    print(f"  - 风控规则: 4层熔断机制")
    print("\n" + "=" * 70)
    print("准备进入 Phase 5: SKILL超级迭代")
    print("=" * 70)
    
    return output

if __name__ == "__main__":
    main()
