#!/usr/bin/env python3
"""
A5L三市场模拟交易计划文档自动更新系统

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

from finnhub_client import FinnhubDataSource
from data_unified import get_data_source
from datetime import datetime
import json


class TradingPlanDocumentUpdater:
    """交易计划文档自动更新器 (带Finnhub限流控制)"""
    
    def __init__(self):
        self.markets = ['CN', 'HK', 'US']
        self.base_path = '/workspace/projects/workspace/data/simulation'
        # 启用限流控制 (80%安全余量: 48次/分钟)
        self.finnhub = FinnhubDataSource(enable_rate_limit=True)
        self.tushare = get_data_source()
    
    def update_all_documents(self):
        """更新所有市场的交易计划文档"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始更新三市场交易计划文档...")
        print(f"   Finnhub限流控制: 已启用 (最多48次/分钟, 安全余量80%)")
        
        for market in self.markets:
            self._update_market_document(market)
        
        # 打印限流统计
        self.finnhub.print_rate_limit_status()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 文档更新完成！")
    
    def _update_market_document(self, market):
        """更新单个市场的交易计划文档"""
        config_file = f'{self.base_path}/{market}_SIM_001.json'
        doc_file = f'{self.base_path}/plans/{market}_SIM_001_LIVE_STATUS.md'
        
        if not os.path.exists(config_file):
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # 获取最新市场数据
        market_data = self._get_market_data(market, config)
        
        # 生成文档内容
        content = self._generate_document(market, config, market_data)
        
        # 保存文档
        with open(doc_file, 'w') as f:
            f.write(content)
        
        print(f"   ✅ {market}_SIM_001 文档已更新")
    
    def _get_market_data(self, market, config):
        """获取市场实时数据"""
        data = {
            'positions': [],
            'total_value': config['cash'],
            'total_pnl': 0
        }
        
        for symbol, pos in config.get('positions', {}).items():
            try:
                if market == 'US':
                    quote = self.finnhub.get_quote(symbol)
                    current_price = quote.get('current', pos['current_price']) if quote else pos['current_price']
                else:
                    # A股和港股通过Tushare
                    quote = self.tushare.get_a_share_realtime(symbol) if market == 'CN' else None
                    current_price = quote.get('close', pos['current_price']) if quote else pos['current_price']
                
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
            except Exception as e:
                print(f"      ⚠️ 获取{symbol}数据失败: {e}")
        
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


def main():
    """主函数"""
    updater = TradingPlanDocumentUpdater()
    updater.update_all_documents()


if __name__ == '__main__':
    main()
