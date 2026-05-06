#!/usr/bin/env python3
"""
A5L三市场模拟交易计划文档自动更新系统

架构整改后版本 - 使用统一数据访问层
⚠️ 禁止直接读取JSON文件，必须通过 unified_position_manager

更新频率控制:
- 推荐: 每15分钟更新一次 (Finnhub API限流: 60次/分钟)
- 美股监控: 8只股票 × 4次/小时 = 32次API调用/小时
- 安全余量: 95% (远低于60次/分钟限制)

Chief设置: 每15分钟自动更新
"""

import sys
import os
import time
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from unified_data_source_manager import UnifiedDataSourceManager
from unified_position_manager import get_position_manager  # 架构整改：统一数据访问层
from datetime import datetime
import json


class TradingPlanDocumentUpdater:
    """交易计划文档自动更新器 (架构整改后版本)"""
    
    def __init__(self):
        self.markets = ['CN', 'HK', 'US']
        self.base_path = '/workspace/projects/workspace/data/simulation'
        # 使用统一数据源管理器 (多API互为保障)
        self.data_manager = UnifiedDataSourceManager(enable_cache=True, cache_duration=300)
        # 架构整改：使用统一持仓管理器（单一真相源）
        self.position_manager = get_position_manager()
    
    def update_all_documents(self):
        """更新所有市场的交易计划文档"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始更新三市场交易计划文档...")
        print(f"   数据源互为保障: 已启用")
        
        # 收集三市场数据
        all_market_data = {}
        for market in self.markets:
            self._update_market_document(market)
            # 读取数据用于汇总看板
            config_file = f'{self.base_path}/{market}_SIM_001.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    all_market_data[market] = json.load(f)
        
        # 更新汇总看板
        self._update_summary_dashboard(all_market_data)
        
        # 打印健康报告
        self.data_manager.print_health_report()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 文档更新完成！")
    
    def _update_summary_dashboard(self, all_market_data):
        """更新汇总看板飞书文档 - 保存为本地MD文件供手动同步"""
        print(f"   📊 更新汇总看板...")
        
        try:
            # 汇总看板本地文件路径
            dashboard_file = f'{self.base_path}/plans/DASHBOARD_SUMMARY.md'
            
            # 生成汇总看板内容
            content = self._generate_dashboard_content(all_market_data)
            
            # 保存到本地文件
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ 汇总看板本地文件已更新: {dashboard_file}")
            print(f"   ⚠️ 飞书文档需手动同步或等待自动同步")
            
            # 尝试通过API更新（可选）
            self._try_update_feishu_dashboard(content)
                
        except Exception as e:
            print(f"   ⚠️ 汇总看板更新异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _try_update_feishu_dashboard(self, content):
        """尝试更新飞书汇总看板（通过FeishuDocUpdater）"""
        try:
            sys.path.insert(0, '/workspace/projects/workspace/tools')
            from feishu_doc_updater import FeishuDocUpdater
            
            updater = FeishuDocUpdater()
            result = updater.update_document(
                doc_id='Jn3ldHm53ormeixxauGcYmkrnLb',
                markdown_content=content[:50000]
            )
            
            if result.get('success'):
                print(f"   ✅ 飞书汇总看板已自动同步")
            else:
                print(f"   ℹ️ 飞书同步: {result.get('message', '未成功')}")
                print(f"   💡 汇总看板本地文件已更新，可手动同步到飞书")
                
        except Exception as e:
            print(f"   ℹ️ 飞书自动同步不可用: {str(e)[:60]}")
            print(f"   💡 汇总看板本地文件已更新: data/simulation/plans/DASHBOARD_SUMMARY.md")
    
    def _update_market_document(self, market):
        """更新单个市场的交易计划文档 - 架构整改后使用统一数据访问层"""
        doc_file = f'{self.base_path}/plans/{market}_SIM_001_LIVE_STATUS.md'
        
        try:
            # 架构整改：使用统一持仓管理器读取数据（单一真相源）
            unified_data = self.position_manager.get_positions(market)
            config = unified_data  # 统一数据格式直接作为配置
            
            # 获取最新市场数据（价格更新）
            market_data = self._get_market_data(market, config)
            
            # 生成文档内容
            content = self._generate_document(market, config, market_data)
            
            # 保存文档
            with open(doc_file, 'w') as f:
                f.write(content)
                
            print(f"   ✅ {market}_SIM_001 文档已更新")
            
        except FileNotFoundError:
            print(f"   ⚠️ {market}_SIM_001 数据文件不存在，跳过")
        except Exception as e:
            print(f"   ⚠️ {market}_SIM_001 更新失败: {e}")
        
        print(f"   ✅ {market}_SIM_001 文档已更新")
    
    def _get_market_data(self, market, config):
        """获取市场实时数据 (多数据源互为保障)"""
        data = {
            'positions': [],
            'total_value': config['cash'],
            'total_pnl': 0
        }
        
        positions = config.get('positions', {})
        if not positions:
            return data
        
        # 批量获取价格 (使用统一数据源管理器)
        symbols = list(positions.keys())
        print(f"      📊 获取{len(symbols)}只股票价格...")
        
        price_results = self.data_manager.get_prices_batch(symbols)
        
        for symbol, pos in positions.items():
            price_data = price_results.get(symbol)
            
            if price_data and price_data.current > 0:
                current_price = price_data.current
                source = price_data.source
                is_cached = "(缓存)" if price_data.is_cached else ""
                print(f"         {symbol}: {current_price} ({source}){is_cached}")
            else:
                # 使用上次已知价格
                current_price = pos.get('current_price', pos['cost_basis'])
                print(f"         {symbol}: 使用上次价格 {current_price} (数据获取失败)")
            
            market_value = current_price * pos['quantity']
            pnl = (current_price - pos['cost_basis']) * pos['quantity']
            pnl_pct = ((current_price - pos['cost_basis']) / pos['cost_basis']) * 100 if pos['cost_basis'] > 0 else 0
            
            data['positions'].append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'cost_basis': pos['cost_basis'],
                'current_price': current_price,
                'market_value': market_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })
            
            data['total_value'] += market_value
            data['total_pnl'] += pnl
        
        return data
    
    def _generate_document(self, market, config, market_data):
        """生成文档内容"""
        currency_map = {'CN': '¥', 'HK': 'HK$', 'US': '$'}
        currency = currency_map.get(market, '$')
        
        total_pnl_pct = (market_data['total_pnl'] / config['initial_capital']) * 100 if config['initial_capital'] > 0 else 0
        
        # 持仓明细
        positions_table = ""
        if market_data['positions']:
            positions_table += "| 标的 | 数量 | 成本价 | 现价 | 市值 | 盈亏 |\n"
            positions_table += "|:----:|:----:|:------:|:----:|:----:|:----:|\n"
            for pos in market_data['positions']:
                emoji = "🟢" if pos['pnl'] > 0 else "🔴"
                positions_table += f"| {emoji} {pos['symbol']} | {pos['quantity']} | {currency}{pos['cost_basis']:.2f} | {currency}{pos['current_price']:.2f} | {currency}{pos['market_value']:,.2f} | {pos['pnl_pct']:+.2f}% |\n"
        else:
            positions_table = "暂无持仓\n"
        
        # 最近交易记录
        recent_trades = config.get('trades', [])[-5:]  # 最近5笔
        trades_table = ""
        if recent_trades:
            trades_table += "| 时间 | 标的 | 方向 | 数量 | 价格 | 盈亏 |\n"
            trades_table += "|:----:|:----:|:----:|:----:|:----:|:----:|\n"
            for trade in recent_trades:
                pnl = trade.get('realized_pnl', 0)
                pnl_str = f"{pnl:+.2f}" if 'realized_pnl' in trade else "-"
                trades_table += f"| {trade['time'][:16]} | {trade['symbol']} | {trade['action']} | {trade['quantity']} | {currency}{trade['price']:.2f} | {pnl_str} |\n"
        else:
            trades_table = "暂无交易记录\n"
        
        # 生成每日复盘（收盘后）
        daily_review = self._generate_daily_review(market, config, market_data, currency)
        
        content = f"""# {market}_SIM_001 实时交易计划文档

> 🔄 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> ⏰ 自动更新频率: 每小时  
> 📊 数据来源: Finnhub (美股) / Tushare (A股港股)

---

## 📈 账户概览

| 项目 | 数值 |
|:----:|:----:|
| **初始资金** | {currency}{config['initial_capital']:,.2f} |
| **当前现金** | {currency}{config['cash']:,.2f} |
| **持仓市值** | {currency}{market_data['total_value'] - config['cash']:,.2f} |
| **总资产** | {currency}{market_data['total_value']:,.2f} |
| **总盈亏** | {currency}{market_data['total_pnl']:,.2f} ({total_pnl_pct:+.2f}%) |
| **持仓数量** | {len(market_data['positions'])} 个标的 |
| **交易次数** | {len(config.get('trades', []))} 笔 |

---

## 💼 当前持仓

{positions_table}

---

## 📋 最近交易记录

{trades_table}

---

## 📝 每日交易复盘

{daily_review}

---

## 🎯 关注列表

**当前关注**: {', '.join(config.get('watchlist', [])[:20])}{'...' if len(config.get('watchlist', [])) > 20 else ''}

---

## 📝 交易规则

- 最大持仓数: {config.get('trading_rules', {}).get('max_positions', 50)} 个标的
- 最大仓位: {config.get('trading_rules', {}).get('max_position_size_pct', 15)}%
- 默认止损: {config.get('trading_rules', {}).get('default_stop_loss_pct', 8)}%
- 默认止盈: {config.get('trading_rules', {}).get('default_take_profit_pct', 15)}%

---

## 🔄 快速操作

```python
# 买入示例
from data.simulation.a5l_unified_trader import {market.lower()}_buy
{market.lower()}_buy('标的代码', 金额, '交易逻辑')

# 卖出示例
from data.simulation.a5l_unified_trader import {market.lower()}_sell
{market.lower()}_sell('标的代码', 数量, '卖出逻辑')
```

---

## 📚 历史交易计划

查看完整交易计划文档:
- 目录: `data/simulation/plans/`
- 命名格式: `{market}-PLAN-YYYYMMDD-XXX.md`

---

*本文档由A5L自动更新系统生成*  
*下次更新: {datetime.now().strftime('%H')}:{(datetime.now().minute + 60) % 60:02d}*
"""
        
        return content
    
    def _generate_dashboard_content(self, all_market_data):
        """生成汇总看板内容"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 提取各市场数据
        us_data = all_market_data.get('US', {})
        hk_data = all_market_data.get('HK', {})
        cn_data = all_market_data.get('CN', {})
        
        # 计算美股数据
        us_cash = us_data.get('cash', 0)
        us_positions = us_data.get('positions', {})
        us_position_count = len(us_positions)
        us_market_value = sum(p.get('quantity', 0) * p.get('current_price', p.get('cost_basis', 0)) for p in us_positions.values())
        us_total = us_cash + us_market_value
        us_initial = us_data.get('initial_capital', 1000000)
        us_pnl = us_total - us_initial
        us_pnl_pct = (us_pnl / us_initial * 100) if us_initial > 0 else 0
        
        # 计算港股数据
        hk_cash = hk_data.get('cash', 0)
        hk_positions = hk_data.get('positions', {})
        hk_position_count = len(hk_positions)
        hk_market_value = sum(p.get('quantity', 0) * p.get('current_price', p.get('cost_basis', 0)) for p in hk_positions.values())
        hk_total = hk_cash + hk_market_value
        hk_initial = hk_data.get('initial_capital', 5000000)
        hk_pnl = hk_total - hk_initial
        hk_pnl_pct = (hk_pnl / hk_initial * 100) if hk_initial > 0 else 0
        
        # 计算A股数据
        cn_cash = cn_data.get('cash', 0)
        cn_positions = cn_data.get('positions', {})
        cn_position_count = len(cn_positions)
        cn_market_value = sum(p.get('quantity', 0) * p.get('current_price', p.get('cost_basis', 0)) for p in cn_positions.values())
        cn_total = cn_cash + cn_market_value
        cn_initial = cn_data.get('initial_capital', 5000000)
        cn_pnl = cn_total - cn_initial
        cn_pnl_pct = (cn_pnl / cn_initial * 100) if cn_initial > 0 else 0
        
        # 获取最近交易
        us_trades = us_data.get('trades', [])
        recent_trade = us_trades[-1] if us_trades else None
        
        content = f"""> **更新时间**: {now} 自动更新
> **覆盖范围**: 美股+港股+A股
> **更新方式**: 自动同步各市场交易数据

---

## 📅 三市场实时概览

**美股**: 交易中 | 本金$1,000,000 | 现金${us_cash:,.0f} | 持仓市值${us_market_value:,.0f} | 持仓**{us_position_count}只** | [查看详情](https://www.feishu.cn/docx/UwxNdkLXHoB6hYxRAlyc9r7Vnef)

**港股**: 待启动 | 本金HK$5,000,000 | 现金HK${hk_cash:,.0f} | 持仓市值HK${hk_market_value:,.0f} | 持仓**{hk_position_count}只** | [查看详情](https://www.feishu.cn/docx/JHRLduaedosoNvxP0KucB8Vgncf)

**A股**: 待启动 | 本金¥5,000,000 | 现金¥{cn_cash:,.0f} | 持仓市值¥{cn_market_value:,.0f} | 持仓**{cn_position_count}只** | [查看详情](https://www.feishu.cn/docx/QxWpdEqnOoEM6zx6MLCck38fnug)

---

## 📊 账户总览

| 市场 | 初始本金 | 当前权益 | 今日盈亏 | 累计盈亏 | 持仓数 |
|------|:--------:|:--------:|:--------:|:--------:|:------:|
| 美股 | $1M | ${us_total:,.0f} | ${us_pnl:,.0f} ({us_pnl_pct:+.2f}%) | ${us_pnl:,.0f} ({us_pnl_pct:+.2f}%) | {us_position_count} |
| 港股 | HK$5M | HK${hk_total:,.0f} | HK${hk_pnl:,.0f} ({hk_pnl_pct:+.2f}%) | HK${hk_pnl:,.0f} ({hk_pnl_pct:+.2f}%) | {hk_position_count} |
| A股 | ¥5M | ¥{cn_total:,.0f} | ¥{cn_pnl:,.0f} ({cn_pnl_pct:+.2f}%) | ¥{cn_pnl:,.0f} ({cn_pnl_pct:+.2f}%) | {cn_position_count} |

---

## 🎯 最近交易
"""
        
        if recent_trade:
            content += f"""
**美股** - {recent_trade.get('time', 'N/A')[:16]}
- 买入 {recent_trade.get('symbol', 'N/A')} {recent_trade.get('quantity', 0)}股 @ ${recent_trade.get('price', 0)}

"""
        else:
            content += "\n暂无最近交易记录\n\n"
        
        content += f"""---

## 🔄 自动更新说明

- **美股**: 每15分钟自动更新 (Finnhub实时数据)
- **港股**: 每30分钟自动更新 (Tushare/Yahoo)
- **A股**: 每30分钟自动更新 (Tushare/AKShare)
- **汇总看板**: 每小时自动同步

---

*CIO三市场模拟交易汇总看板*  
**自动更新** | **下次更新**: {(datetime.now().hour + 1) % 24}:{datetime.now().minute:02d}

---

## 🔗 相关文档

- **美股交易计划**: https://www.feishu.cn/docx/UwxNdkLXHoB6hYxRAlyc9r7Vnef
- **港股交易计划**: https://www.feishu.cn/docx/JHRLduaedosoNvxP0KucB8Vgncf
- **A股交易计划**: https://www.feishu.cn/docx/QxWpdEqnOoEM6zx6MLCck38fnug
- **NVDA首笔交易**: https://www.feishu.cn/docx/V3vpdVeSHoaoBXx3zgdcuos7nee
"""
        
        return content
    
    def _generate_daily_review(self, market, config, market_data, currency):
        """生成每日交易复盘"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取今日交易（从昨日收盘到今日收盘）
        all_trades = config.get('trades', [])
        today_trades = []
        
        for trade in all_trades:
            trade_time = trade.get('time', '')
            if today in trade_time:
                today_trades.append(trade)
        
        if not today_trades:
            return f"""**{today} 无交易记录**

今日未执行任何交易操作。

---

**持仓状态**: 持有 {len(market_data['positions'])} 个标的

**明日关注**: 等待交易机会
"""
        
        # 生成每笔交易的复盘
        review_sections = []
        total_pnl_today = 0
        
        for i, trade in enumerate(today_trades, 1):
            symbol = trade.get('symbol', 'N/A')
            action = trade.get('action', 'BUY')
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            plan_id = trade.get('plan_id', 'N/A')
            notes = trade.get('notes', '')
            
            # 获取当前持仓信息（如果还在持仓）
            current_pos = None
            for pos in market_data['positions']:
                if pos['symbol'] == symbol:
                    current_pos = pos
                    break
            current_price = current_pos['current_price'] if current_pos else price
            unrealized_pnl = current_pos['pnl'] if current_pos else 0
            
            # 计算盈亏比（如果是卖出交易）
            realized_pnl = trade.get('realized_pnl', 0)
            if realized_pnl != 0:
                pnl_status = f"已实现盈亏: {currency}{realized_pnl:+.2f}"
            else:
                pnl_status = f"浮动盈亏: {currency}{unrealized_pnl:+.2f}"
            
            # 构建复盘段落
            review_section = f"""### 交易 #{i}: {symbol} ({action})

**交易详情**:
- 时间: {trade.get('time', 'N/A')[:16]}
- 数量: {quantity} 股
- 价格: {currency}{price:.2f}
- 金额: {currency}{amount:,.2f}
- {pnl_status}

**买入原因/交易逻辑**:
{notes if notes else '• 追涨策略测试' if '追涨' in notes else '• 均值回归测试' if '均值回归' in notes else '• 突破策略测试' if '突破' in notes else '• 策略测试'}

**预期目标**:
- 目标价: {currency}{price * 1.15:.2f} (+15%)
- 止损价: {currency}{price * 0.92:.2f} (-8%)
- 预期持仓: 3-5天

**复盘分析**:
- **是否达到预期**: {'已达到' if realized_pnl > 0 else '持仓中' if action == 'BUY' and current_pos else '已止损/止盈'}
- **预期差分析**: {f'价格已上涨 {(current_price/price-1)*100:.1f}%，接近目标' if current_price > price else f'价格回调 {(1-current_price/price)*100:.1f}%，需观察'}
- **盈亏比**: {f'{abs(realized_pnl)/amount*100:.1f}%' if realized_pnl != 0 else f'{abs(unrealized_pnl)/amount*100:.1f}% (浮动)'}
- **模式归类**: {'趋势跟踪' if '追涨' in notes else '均值回归' if '均值回归' in notes else '突破交易' if '突破' in notes else '策略测试'}

---
"""
            review_sections.append(review_section)
            total_pnl_today += realized_pnl if realized_pnl != 0 else unrealized_pnl
        
        # 生成汇总
        review_content = f"""### 📊 {today} 交易汇总

**今日交易**: {len(today_trades)} 笔  
**今日盈亏**: {currency}{total_pnl_today:+.2f}  
**胜率**: {'待平仓后统计' if any(t.get('action') == 'BUY' for t in today_trades) else '100%' if total_pnl_today > 0 else '0%'}

---

"""
        
        review_content += "\n".join(review_sections)
        
        # 添加经验教训
        review_content += f"""
### 💡 经验教训

**成功之处**:
- {'把握了市场节奏，在合适价位建仓' if total_pnl_today >= 0 else '及时止损，控制了风险'}

**需要改进**:
- {'持仓集中度需要关注' if len(market_data['positions']) > 3 else '可以更加果断执行交易计划'}

**明日计划**:
- 继续持有观察标的走势
- 严格执行止损止盈纪律
- 关注市场情绪和资金流向

---

*复盘生成时间: {datetime.now().strftime('%H:%M:%S')}*  
*下次更新: 收盘后自动生成*
"""
        
        return review_content


def main():
    """主函数"""
    updater = TradingPlanDocumentUpdater()
    updater.update_all_documents()


if __name__ == '__main__':
    main()
