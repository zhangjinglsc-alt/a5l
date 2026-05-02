#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L CLI - 命令行工具
让A5L可以通过终端直接调用

使用方法:
    a5l --help                    # 查看帮助
    a5l analyze AAPL              # 分析股票
    a5l trade buy AAPL 10 180.5   # 执行模拟交易
    a5l portfolio                 # 查看投资组合
    a5l review                    # 运行每日复盘
    a5l pipeline 000001.SZ        # 执行完整流水线
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import Optional

sys.path.insert(0, "/workspace/projects/workspace")

class A5LCLI:
    """A5L命令行界面"""
    
    def __init__(self):
        self.skill = None
        self._init_skill()
    
    def _init_skill(self):
        """初始化A5L SKILL"""
        try:
            # 动态导入避免连字符问题
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "SKILL", 
                "/workspace/projects/workspace/skills/ARCHITECT-5L-SUPER/SKILL.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            Architect5LSuperSkill = module.Architect5LSuperSkill
            self.skill = Architect5LSuperSkill()
            print("✅ A5L初始化完成")
        except Exception as e:
            print(f"⚠️ A5L初始化警告: {e}")
            print("部分功能可能不可用")
    
    def analyze(self, symbol: str, detailed: bool = False):
        """分析股票"""
        print(f"\n🔍 分析股票: {symbol}")
        print("-" * 60)
        
        if not self.skill:
            print("❌ A5L未初始化")
            return
        
        try:
            result = self.skill.execute_full_pipeline(symbol)
            
            print(f"\n📊 分析结果:")
            print(f"  股票代码: {result['symbol']}")
            print(f"  分析时间: {result['timestamp']}")
            print()
            
            # Layer 1
            if 'layer1_data' in result['pipeline']:
                l1 = result['pipeline']['layer1_data']
                print(f"  📈 Layer 1 - 数据感知:")
                print(f"    状态: {l1['status']}")
                print(f"    数据条数: {l1['records']}")
            
            # Layer 2
            if 'layer2_strategy' in result['pipeline']:
                l2 = result['pipeline']['layer2_strategy']
                print(f"\n  🎯 Layer 2 - 策略信号:")
                print(f"    信号数量: {l2['signals_count']}")
                if l2.get('signals'):
                    for sig in l2['signals'][:3]:
                        print(f"    • {sig.get('strategy')}: {sig.get('action')} (置信度: {sig.get('confidence', 0):.0%})")
            
            # Layer 3
            if 'layer3_cognitive' in result['pipeline']:
                l3 = result['pipeline']['layer3_cognitive']
                print(f"\n  🧠 Layer 3 - 认知分析:")
                print(f"    情绪得分: {l3.get('sentiment', 'N/A')}")
                print(f"    新闻数量: {l3['news_count']}")
            
            # Layer 4
            if 'layer4_execution' in result['pipeline']:
                l4 = result['pipeline']['layer4_execution']
                print(f"\n  ⚡ Layer 4 - 决策执行:")
                decision = l4.get('decision', {})
                print(f"    建议操作: {decision.get('action', 'HOLD')}")
                print(f"    策略: {decision.get('strategy', 'N/A')}")
            
            if detailed:
                print(f"\n📋 完整结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    def trade(self, action: str, symbol: str, quantity: int, 
              price: float, strategy: str = "cli", account: str = "US_SIM_001"):
        """执行模拟交易"""
        print(f"\n🎮 执行模拟交易")
        print("-" * 60)
        
        if not self.skill:
            print("❌ A5L未初始化")
            return
        
        try:
            # 映射动作
            action_map = {
                "buy": "BUY",
                "sell": "SELL",
                "买入": "BUY",
                "卖出": "SELL"
            }
            action = action_map.get(action.lower(), action.upper())
            
            result = self.skill.execute_simulated_trade(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                strategy=strategy,
                confidence=0.8,
                account_id=account
            )
            
            if result.get("success"):
                print(f"✅ 交易执行成功!")
                print(f"  交易ID: {result['trade_id']}")
                print(f"  标的: {symbol}")
                print(f"  动作: {action}")
                print(f"  数量: {quantity}")
                print(f"  价格: ${price:.2f}")
                print(f"  交易成本: ${result['costs'].get('total', 0):.2f}")
                print(f"  可用现金: ${result['account'].get('available_cash', 0):.2f}")
            else:
                print(f"❌ 交易失败: {result.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"❌ 交易执行失败: {e}")
    
    def portfolio(self, account: Optional[str] = None):
        """查看投资组合"""
        print(f"\n📊 投资组合概况")
        print("-" * 60)
        
        if not self.skill:
            print("❌ A5L未初始化")
            return
        
        try:
            portfolios = self.skill.get_simulated_portfolio(account)
            
            if account:
                portfolios = {account: portfolios}
            
            for acc_id, portfolio in portfolios.items():
                if isinstance(portfolio, dict) and 'error' not in portfolio:
                    print(f"\n  💼 {portfolio.get('account_name', acc_id)}")
                    print(f"  市场: {portfolio.get('market', 'N/A')}")
                    print(f"  初始资金: ${portfolio.get('initial_capital', 0):,.2f}")
                    print(f"  可用现金: ${portfolio.get('available_cash', 0):,.2f}")
                    print(f"  总资产: ${portfolio.get('total_equity', 0):,.2f}")
                    print(f"  收益率: {portfolio.get('total_return', 0):.2f}%")
                    print(f"  持仓数: {portfolio.get('positions_count', 0)}")
                    
                    if portfolio.get('positions'):
                        print(f"\n  当前持仓:")
                        for symbol, pos in portfolio['positions'].items():
                            print(f"    • {symbol}: {pos.get('quantity')}股 @ 均价${pos.get('avg_price', 0):.2f}")
                else:
                    print(f"  ⚠️ {acc_id}: 获取失败")
        
        except Exception as e:
            print(f"❌ 获取投资组合失败: {e}")
    
    def review(self, date: Optional[str] = None, account: Optional[str] = None):
        """运行每日复盘"""
        print(f"\n🔄 每日交易复盘")
        print("-" * 60)
        
        if not self.skill:
            print("❌ A5L未初始化")
            return
        
        try:
            report = self.skill.run_daily_trading_review(date, account)
            
            if 'error' in report:
                print(f"❌ 复盘失败: {report['error']}")
                return
            
            print(f"\n📅 复盘日期: {report['date']}")
            print(f"📊 交易统计:")
            print(f"  总交易数: {report['total_trades']}")
            print(f"  盈利交易: {report['winning_trades']}")
            print(f"  亏损交易: {report['losing_trades']}")
            print(f"  胜率: {report['win_rate']*100:.1f}%")
            print()
            print(f"💰 绩效指标:")
            print(f"  总盈亏: ${report['total_pnl']:,.2f}")
            print(f"  平均盈利: ${report['avg_profit']:,.2f}")
            print(f"  平均亏损: ${report['avg_loss']:,.2f}")
            print(f"  盈亏比: {report['profit_factor']:.2f}")
            
            if report.get('strategy_performance'):
                print(f"\n🎯 策略绩效:")
                for strategy, stats in report['strategy_performance'].items():
                    print(f"  • {strategy}: {stats['trades']}笔, 胜率{stats['win_rate']*100:.0f}%")
            
            print(f"\n📝 复盘总结: {report['summary']}")
            
            if report.get('action_items'):
                print(f"\n✅ 行动项:")
                for i, item in enumerate(report['action_items'], 1):
                    print(f"  {i}. {item}")
        
        except Exception as e:
            print(f"❌ 复盘失败: {e}")
    
    def kiwi(self, action: str, **kwargs):
        """KIWI知识中心操作"""
        print(f"\n📚 KIWI知识中心")
        print("-" * 60)
        
        if not self.skill:
            print("❌ A5L未初始化")
            return
        
        try:
            if action == "archive":
                result = self.skill.archive_to_kiwi(
                    title=kwargs.get('title', ''),
                    content=kwargs.get('content', ''),
                    knowledge_type=kwargs.get('type', 'analysis'),
                    entities=kwargs.get('entities', []),
                    tags=kwargs.get('tags', [])
                )
                print(f"✅ 知识已归档: {result.get('knowledge_id')}")
            
            elif action == "query":
                results = self.skill.query_kiwi(
                    query=kwargs.get('query', ''),
                    query_type=kwargs.get('type', 'keyword'),
                    limit=kwargs.get('limit', 10)
                )
                print(f"🔍 查询结果: {len(results.get('results', []))}条")
                for r in results.get('results', [])[:5]:
                    print(f"  • {r.get('title')} (相关度: {r.get('relevance', 0):.2f})")
            
            elif action == "stats":
                stats = self.skill.get_kiwi_stats()
                print(f"📊 KIWI统计:")
                print(f"  总知识数: {stats.get('total_knowledge', 0)}")
                print(f"  实体数: {stats.get('total_entities', 0)}")
                print(f"  关系数: {stats.get('total_relations', 0)}")
        
        except Exception as e:
            print(f"❌ KIWI操作失败: {e}")
    
    def status(self):
        """查看A5L状态"""
        print(f"\n🏗️ A5L系统状态")
        print("-" * 60)
        print(f"版本: v1.0.0")
        print(f"架构: ARCHITECT-5L (7层)")
        print(f"初始化: {'✅ 完成' if self.skill else '❌ 失败'}")
        print()
        print("各层状态:")
        print("  ✅ Layer 0: 元控制层 (七位一体)")
        print("  ✅ Layer 1: 数据感知层")
        print("  ✅ Layer 2: 策略决策层 (7策略)")
        print("  ✅ Layer 3: 认知分析层")
        print("  ✅ Layer 4: 执行控制层 (模拟交易)")
        print("  ✅ Layer 5: 元学习层 (自动复盘)")
        print()
        print("核心功能:")
        print("  • 模拟交易: 美股/A股/港股")
        print("  • 自动复盘: 每日21:00")
        print("  • 知识中心: KIWI")
        print("  • 多模态处理: 6种类型")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="A5L CLI - ARCHITECT-5L Super Skill 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  a5l analyze AAPL                    # 分析苹果公司
  a5l analyze 000001.SZ --detailed    # 详细分析平安银行
  a5l trade buy AAPL 10 180.5         # 买入10股AAPL
  a5l portfolio                       # 查看所有账户
  a5l portfolio --account US_SIM_001  # 查看美股账户
  a5l review                          # 昨日复盘
  a5l review --date 2026-05-01        # 指定日期复盘
  a5l kiwi archive --title "分析"      # 归档知识
  a5l kiwi query --query "宁德时代"    # 查询知识
  a5l status                          # 查看系统状态
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze命令
    analyze_parser = subparsers.add_parser('analyze', help='分析股票')
    analyze_parser.add_argument('symbol', help='股票代码 (如: AAPL, 000001.SZ)')
    analyze_parser.add_argument('--detailed', '-d', action='store_true', help='显示详细信息')
    
    # trade命令
    trade_parser = subparsers.add_parser('trade', help='执行模拟交易')
    trade_parser.add_argument('action', choices=['buy', 'sell', '买入', '卖出'], help='交易动作')
    trade_parser.add_argument('symbol', help='股票代码')
    trade_parser.add_argument('quantity', type=int, help='交易数量')
    trade_parser.add_argument('price', type=float, help='交易价格')
    trade_parser.add_argument('--strategy', '-s', default='cli', help='策略名称')
    trade_parser.add_argument('--account', '-a', default='US_SIM_001', help='账户ID')
    
    # portfolio命令
    portfolio_parser = subparsers.add_parser('portfolio', help='查看投资组合')
    portfolio_parser.add_argument('--account', '-a', help='指定账户 (默认全部)')
    
    # review命令
    review_parser = subparsers.add_parser('review', help='运行每日复盘')
    review_parser.add_argument('--date', '-d', help='复盘日期 (YYYY-MM-DD, 默认昨天)')
    review_parser.add_argument('--account', '-a', help='指定账户')
    
    # kiwi命令
    kiwi_parser = subparsers.add_parser('kiwi', help='KIWI知识中心')
    kiwi_subparsers = kiwi_parser.add_subparsers(dest='kiwi_action', help='KIWI操作')
    
    # kiwi archive
    kiwi_archive = kiwi_subparsers.add_parser('archive', help='归档知识')
    kiwi_archive.add_argument('--title', required=True, help='知识标题')
    kiwi_archive.add_argument('--content', required=True, help='知识内容')
    kiwi_archive.add_argument('--type', default='analysis', help='知识类型')
    
    # kiwi query
    kiwi_query = kiwi_subparsers.add_parser('query', help='查询知识')
    kiwi_query.add_argument('--query', '-q', required=True, help='查询内容')
    kiwi_query.add_argument('--type', default='keyword', help='查询类型')
    kiwi_query.add_argument('--limit', '-l', type=int, default=10, help='结果数量')
    
    # kiwi stats
    kiwi_stats = kiwi_subparsers.add_parser('stats', help='查看统计')
    
    # status命令
    status_parser = subparsers.add_parser('status', help='查看系统状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = A5LCLI()
    
    if args.command == 'analyze':
        cli.analyze(args.symbol, args.detailed)
    
    elif args.command == 'trade':
        cli.trade(args.action, args.symbol, args.quantity, 
                 args.price, args.strategy, args.account)
    
    elif args.command == 'portfolio':
        cli.portfolio(args.account)
    
    elif args.command == 'review':
        cli.review(args.date, args.account)
    
    elif args.command == 'kiwi':
        if args.kiwi_action == 'archive':
            cli.kiwi('archive', title=args.title, content=args.content, type=args.type)
        elif args.kiwi_action == 'query':
            cli.kiwi('query', query=args.query, type=args.type, limit=args.limit)
        elif args.kiwi_action == 'stats':
            cli.kiwi('stats')
        else:
            kiwi_parser.print_help()
    
    elif args.command == 'status':
        cli.status()
    
    print()  # 空行结尾

if __name__ == '__main__':
    main()
