#!/usr/bin/env python3
"""
A5L三市场统一交易执行系统 v1.0
支持CN_SIM_001 (A股) + HK_SIM_001 (港股) + US_SIM_001 (美股)

Chief指导: "放开标的限制，大胆试错，全面记录，不断修正直到找到盈利模式"

交易理念:
- 试错 → 记录 → 分析 → 修正 → 盈利
- 批量交易，大量交割单，大量复盘
- 三市场统一范式，完整归因
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from data_unified import get_data_source
from finnhub_client import FinnhubDataSource
from datetime import datetime
import json


class A5LUnifiedTrader:
    """
    A5L三市场统一交易执行系统
    - 支持A股 (CN_SIM_001)
    - 支持港股 (HK_SIM_001)
    - 支持美股 (US_SIM_001)
    - 统一交易范式
    - 完整归因记录
    """
    
    def __init__(self, market='CN'):
        """
        初始化交易系统
        
        Args:
            market: 'CN' (A股) / 'HK' (港股) / 'US' (美股)
        """
        self.market = market.upper()
        self.config_file = f'/workspace/projects/workspace/data/simulation/{market}_SIM_001.json'
        self.config = self._load_config()
        
        # 初始化数据源
        if market in ['CN', 'HK']:
            self.data_source = get_data_source()
        else:  # US
            self.data_source = FinnhubDataSource()
    
    def _load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        currency_map = {'CN': 'CNY', 'HK': 'HKD', 'US': 'USD'}
        return {
            'account': f'{self.market}_SIM_001',
            'currency': currency_map.get(self.market, 'USD'),
            'initial_capital': 5000000.0 if self.market != 'US' else 1000000.0,
            'current_equity': 5000000.0 if self.market != 'US' else 1000000.0,
            'cash': 5000000.0 if self.market != 'US' else 1000000.0,
            'positions': {},
            'trades': [],
            'watchlist': [],
            'trading_rules': {
                'max_positions': 50,
                'max_position_size_pct': 15,
                'max_single_loss_pct': 5,
                'default_stop_loss_pct': 8,
                'default_take_profit_pct': 15,
                'record_required': True
            },
            'experiment_log': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'strategies_tested': [],
                'lessons_learned': []
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'status': 'active',
            'market': self.market,
            'strategy': 'aggressive_experimentation',
            'notes': 'Chief指导:放开标的限制，大胆试错，全面记录，不断修正'
        }
    
    def save_config(self):
        """保存配置"""
        self.config['last_updated'] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_symbols(self, symbols):
        """添加标的到关注列表"""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol not in self.config['watchlist']:
                self.config['watchlist'].append(symbol)
                print(f"   ✅ [{self.market}] 已添加 {symbol}")
        
        self.save_config()
    
    def execute_trade(self, symbol, action, quantity, price, reasoning=""):
        """执行交易"""
        symbol = symbol.upper()
        amount = quantity * price
        
        # 检查资金
        if action == 'BUY' and amount > self.config['cash']:
            print(f"   ❌ [{self.market}] 资金不足")
            return None
        
        # 生成ID
        trade_num = len(self.config['trades']) + 1
        trade_id = f"{self.market}-TRADE-{trade_num:04d}"
        plan_id = f"{self.market}-PLAN-{datetime.now().strftime('%Y%m%d')}-{trade_num:04d}"
        
        # 创建交易记录
        trade = {
            'trade_id': trade_id,
            'plan_id': plan_id,
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'amount': amount,
            'reasoning': reasoning,
            'status': 'executed',
            'market': self.market
        }
        
        # 更新持仓
        if action == 'BUY':
            if symbol in self.config['positions']:
                pos = self.config['positions'][symbol]
                total_cost = pos['cost_basis'] * pos['quantity'] + amount
                total_qty = pos['quantity'] + quantity
                pos['cost_basis'] = total_cost / total_qty
                pos['quantity'] = total_qty
            else:
                self.config['positions'][symbol] = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'cost_basis': price,
                    'current_price': price,
                    'market_value': amount,
                    'unrealized_pnl': 0.0,
                    'unrealized_pnl_pct': 0.0,
                    'entry_time': datetime.now().isoformat()
                }
            self.config['cash'] -= amount
            
        elif action == 'SELL':
            if symbol in self.config['positions']:
                pos = self.config['positions'][symbol]
                if quantity >= pos['quantity']:
                    realized_pnl = (price - pos['cost_basis']) * pos['quantity']
                    trade['realized_pnl'] = realized_pnl
                    del self.config['positions'][symbol]
                else:
                    realized_pnl = (price - pos['cost_basis']) * quantity
                    trade['realized_pnl'] = realized_pnl
                    pos['quantity'] -= quantity
                self.config['cash'] += amount
        
        self.config['trades'].append(trade)
        self._create_trade_plan(trade, reasoning)
        self.save_config()
        
        currency = {'CN': '¥', 'HK': 'HK$', 'US': '$'}[self.market]
        print(f"   ✅ [{self.market}] {action} {quantity}股 {symbol} @ {currency}{price:.2f}")
        return trade
    
    def _create_trade_plan(self, trade, reasoning):
        """创建交易计划文档"""
        plan_id = trade['plan_id']
        plan_file = f"/workspace/projects/workspace/data/simulation/plans/{plan_id}.md"
        
        template_file = "/workspace/projects/workspace/data/simulation/plans/UNIFIED_TRADE_PLAN_TEMPLATE.md"
        if os.path.exists(template_file):
            with open(template_file, 'r') as f:
                template = f.read()
        else:
            template = self._get_simple_template()
        
        # 填充模板
        content = template.replace('{plan_id}', plan_id)
        content = content.replace('{market}', self.market)
        content = content.replace('{create_time}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        content = content.replace('{status}', 'ACTIVE')
        content = content.replace('{symbol}', trade['symbol'])
        content = content.replace('{action}', trade['action'])
        content = content.replace('{quantity}', str(trade['quantity']))
        content = content.replace('{entry_price}', str(trade['price']))
        content = content.replace('{entry_amount}', str(trade['amount']))
        content = content.replace('{entry_time}', trade['time'])
        content = content.replace('{stock_selection_reasoning}', reasoning or "待补充")
        content = content.replace('{record_time}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        with open(plan_file, 'w') as f:
            f.write(content)
    
    def _get_simple_template(self):
        """获取简化模板"""
        return """# 交易计划: {plan_id}

## 基本信息
- 市场: {market}
- 标的: {symbol}
- 方向: {action}
- 数量: {quantity}
- 价格: {entry_price}
- 时间: {entry_time}

## 选股逻辑
{stock_selection_reasoning}

## 风险控制
- 止损: 待设定
- 止盈: 待设定

## 盈亏归因
待平仓后填写

## 复盘记录
待更新

---
记录时间: {record_time}
"""
    
    def get_quote(self, symbol):
        """获取报价"""
        try:
            if self.market == 'CN':
                quote = self.data_source.get_a_share_realtime(symbol)
                return {'current': quote.get('close', 0)} if quote else None
            elif self.market == 'HK':
                # 港股通过Tushare
                import tushare as ts
                pro = ts.pro_api()
                df = pro.hk_daily(ts_code=symbol)
                if not df.empty:
                    return {'current': float(df.iloc[0]['close'])}
                return None
            else:  # US
                return self.data_source.get_quote(symbol)
        except Exception as e:
            print(f"   ⚠️ 获取报价失败: {e}")
            return None
    
    def quick_trade(self, symbol, action, amount, reasoning=""):
        """快速交易 (按金额)"""
        quote = self.get_quote(symbol)
        if not quote:
            print(f"   ❌ 无法获取 {symbol} 报价")
            return None
        
        price = quote.get('current', 0)
        if price <= 0:
            print(f"   ❌ 无效价格: {price}")
            return None
        
        quantity = int(amount / price)
        if quantity < 1:
            currency = {'CN': '¥', 'HK': 'HK$', 'US': '$'}[self.market]
            print(f"   ❌ 金额不足购买1股 {symbol} (当前价 {currency}{price:.2f})")
            return None
        
        return self.execute_trade(symbol, action, quantity, price, reasoning)
    
    def print_portfolio(self):
        """打印持仓"""
        currency = {'CN': '¥', 'HK': 'HK$', 'US': '$'}[self.market]
        
        print(f"\n{'='*70}")
        print(f"{self.market}_SIM_001 持仓摘要")
        print(f"{'='*70}")
        print(f"💰 现金: {currency}{self.config['cash']:,.2f}")
        
        positions_value = 0
        for pos in self.config['positions'].values():
            quote = self.get_quote(pos['symbol'])
            current_price = quote.get('current', pos['current_price']) if quote else pos['current_price']
            market_value = current_price * pos['quantity']
            positions_value += market_value
            
            pnl = (current_price - pos['cost_basis']) * pos['quantity']
            pnl_pct = ((current_price - pos['cost_basis']) / pos['cost_basis']) * 100 if pos['cost_basis'] > 0 else 0
            emoji = "🟢" if pnl > 0 else "🔴"
            
            print(f"{emoji} {pos['symbol']}: {pos['quantity']}股 | "
                  f"成本:{currency}{pos['cost_basis']:.2f} | 现价:{currency}{current_price:.2f} | "
                  f"盈亏:{currency}{pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        total_value = self.config['cash'] + positions_value
        total_pnl = total_value - self.config['initial_capital']
        total_pnl_pct = (total_pnl / self.config['initial_capital']) * 100
        
        print(f"\n💵 总资产: {currency}{total_value:,.2f}")
        print(f"📈 总盈亏: {currency}{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
        print(f"📋 持仓数量: {len(self.config['positions'])} 个标的")
        print(f"{'='*70}\n")
    
    def generate_report(self):
        """生成交易报告"""
        trades = self.config['trades']
        if not trades:
            print(f"[{self.market}] 暂无交易记录")
            return
        
        winning = [t for t in trades if t.get('realized_pnl', 0) > 0]
        losing = [t for t in trades if t.get('realized_pnl', 0) <= 0]
        total_pnl = sum(t.get('realized_pnl', 0) for t in trades)
        
        print(f"\n{'='*70}")
        print(f"{self.market}_SIM_001 交易报告")
        print(f"{'='*70}")
        print(f"总交易次数: {len(trades)}")
        print(f"盈利次数: {len(winning)}")
        print(f"亏损次数: {len(losing)}")
        print(f"胜率: {len(winning)/len(trades)*100:.2f}%" if trades else "胜率: N/A")
        print(f"总盈亏: {total_pnl:,.2f}")
        print(f"{'='*70}\n")


# 快捷函数
def cn_buy(symbol, amount, reasoning=""):
    """A股买入"""
    trader = A5LUnifiedTrader('CN')
    return trader.quick_trade(symbol, 'BUY', amount, reasoning)

def cn_sell(symbol, quantity, reasoning=""):
    """A股卖出"""
    trader = A5LUnifiedTrader('CN')
    return trader.execute_trade(symbol, 'SELL', quantity, 0, reasoning)

def hk_buy(symbol, amount, reasoning=""):
    """港股买入"""
    trader = A5LUnifiedTrader('HK')
    return trader.quick_trade(symbol, 'BUY', amount, reasoning)

def hk_sell(symbol, quantity, reasoning=""):
    """港股卖出"""
    trader = A5LUnifiedTrader('HK')
    return trader.execute_trade(symbol, 'SELL', quantity, 0, reasoning)

def us_buy(symbol, amount, reasoning=""):
    """美股买入"""
    trader = A5LUnifiedTrader('US')
    return trader.quick_trade(symbol, 'BUY', amount, reasoning)

def us_sell(symbol, quantity, reasoning=""):
    """美股卖出"""
    trader = A5LUnifiedTrader('US')
    return trader.execute_trade(symbol, 'SELL', quantity, 0, reasoning)

def portfolio_all():
    """查看所有市场持仓"""
    for market in ['CN', 'HK', 'US']:
        trader = A5LUnifiedTrader(market)
        trader.print_portfolio()

def report_all():
    """查看所有市场交易报告"""
    for market in ['CN', 'HK', 'US']:
        trader = A5LUnifiedTrader(market)
        trader.generate_report()


if __name__ == '__main__':
    print("="*70)
    print("🇨🇳🇭🇰🇺🇸 A5L三市场统一交易执行系统 v1.0")
    print("="*70)
    print()
    print("Chief指导: 放开标的限制，大胆试错，全面记录，不断修正")
    print()
    print("💡 快捷操作:")
    print("   cn_buy('000001', 10000)   - A股买入¥10,000平安银行")
    print("   hk_buy('00700', 10000)    - 港股买入HK$10,000腾讯")
    print("   us_buy('NVDA', 10000)     - 美股买入$10,000 NVDA")
    print("   portfolio_all()            - 查看三市场持仓")
    print("   report_all()               - 查看三市场交易报告")
