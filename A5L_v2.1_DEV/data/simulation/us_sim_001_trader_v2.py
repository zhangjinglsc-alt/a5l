#!/usr/bin/env python3
"""
US_SIM_001 美股模拟交易系统 v2.0 - 放开标的限制版
支持无限制试错，全面记录，不断修正直到找到盈利模式

Chief指导: "放开标的限制，大胆试错，全面记录，不断修正"
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_client import FinnhubDataSource
from finnhub_websocket import FinnhubWebSocketClient
from datetime import datetime, timedelta
import json
import time


class USSim001AggressiveTrader:
    """
    US_SIM_001 激进交易实验系统
    - 放开标的限制 (最多同时持有50个标的)
    - 大胆试错 (允许小额高频交易)
    - 全面记录 (每笔交易都有完整计划)
    - 不断修正 (基于历史数据优化策略)
    """
    
    def __init__(self, config_file=None):
        self.config_file = config_file or '/workspace/projects/workspace/data/simulation/US_SIM_001.json'
        self.config = self._load_config()
        self.finnhub = FinnhubDataSource()
        self.ws_client = None
        self.price_cache = {}
        self.experiment_data = []
        
    def _load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        return {
            "account": "US_SIM_001",
            "currency": "USD",
            "initial_capital": 1000000.0,
            "current_equity": 1000000.0,
            "cash": 1000000.0,
            "positions": {},
            "trades": [],
            "watchlist": [
                # 科技巨头
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META",
                # 半导体
                "INTC", "AMD", "AVGO", "QCOM", "TXN", "MU", "MRVL", "LRCX", "KLAC", "AMAT",
                # 存储
                "WDC", "STX",
                # 软件
                "NFLX", "CRM", "ORCL", "INTU", "ADBE", "SNPS", "CDNS",
                # 金融
                "JPM", "BAC", "GS", "MS", "WFC",
                # 消费
                "WMT", "COST", "HD", "NKE", "DIS",
                # 医药
                "JNJ", "PFE", "UNH", "ABBV", "LLY",
                # 能源
                "XOM", "CVX",
                # ETF
                "SPY", "QQQ", "IWM", "VIX"
            ],
            "trading_rules": {
                "max_positions": 50,  # 最多同时持有50个标的
                "max_position_size_pct": 20,  # 单个标的最大仓位20%
                "max_single_loss_pct": 5,  # 单次最大亏损5%
                "default_stop_loss_pct": 8,
                "default_take_profit_pct": 15,
                "allow_short": True,
                "min_trade_amount": 1000,  # 最小交易金额$1000
                "record_required": True
            }
        }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_to_watchlist(self, symbols):
        """添加标的到关注列表"""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol not in self.config['watchlist']:
                self.config['watchlist'].append(symbol)
                print(f"   ✅ 已添加 {symbol} 到关注列表")
        
        self.save_config()
    
    def execute_trade(self, symbol, action, quantity, price, reasoning=""):
        """
        执行交易
        
        Args:
            symbol: 股票代码
            action: BUY/SELL
            quantity: 数量
            price: 价格
            reasoning: 交易逻辑
        """
        symbol = symbol.upper()
        amount = quantity * price
        
        # 检查资金
        if action == 'BUY' and amount > self.config['cash']:
            print(f"   ❌ 资金不足: 需要${amount:,.2f}, 可用${self.config['cash']:,.2f}")
            return None
        
        # 生成交易ID和计划ID
        trade_id = f"US-TRADE-{len(self.config['trades']) + 1:04d}"
        plan_id = f"US-PLAN-{datetime.now().strftime('%Y%m%d')}-{len(self.config['trades']) + 1:04d}"
        
        # 创建交易记录
        trade = {
            "trade_id": trade_id,
            "plan_id": plan_id,
            "time": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "reasoning": reasoning,
            "status": "executed"
        }
        
        # 更新持仓
        if action == 'BUY':
            if symbol in self.config['positions']:
                # 加仓，更新成本
                pos = self.config['positions'][symbol]
                total_cost = pos['cost_basis'] * pos['quantity'] + amount
                total_qty = pos['quantity'] + quantity
                pos['cost_basis'] = total_cost / total_qty
                pos['quantity'] = total_qty
            else:
                # 新建仓
                self.config['positions'][symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "cost_basis": price,
                    "current_price": price,
                    "market_value": amount,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_pct": 0.0,
                    "entry_time": datetime.now().isoformat()
                }
            
            self.config['cash'] -= amount
            
        elif action == 'SELL':
            if symbol in self.config['positions']:
                pos = self.config['positions'][symbol]
                if quantity >= pos['quantity']:
                    # 清仓
                    realized_pnl = (price - pos['cost_basis']) * pos['quantity']
                    trade['realized_pnl'] = realized_pnl
                    del self.config['positions'][symbol]
                else:
                    # 减仓
                    realized_pnl = (price - pos['cost_basis']) * quantity
                    trade['realized_pnl'] = realized_pnl
                    pos['quantity'] -= quantity
                
                self.config['cash'] += amount
        
        # 保存交易记录
        self.config['trades'].append(trade)
        
        # 创建交易计划文档
        self._create_trade_plan(trade, reasoning)
        
        # 保存配置
        self.save_config()
        
        print(f"   ✅ 交易执行成功: {action} {quantity}股 {symbol} @ ${price:.2f}")
        print(f"   📝 交易计划: {plan_id}")
        
        return trade
    
    def _create_trade_plan(self, trade, reasoning):
        """创建交易计划文档"""
        plan_id = trade['plan_id']
        plan_file = f"/workspace/projects/workspace/data/simulation/plans/{plan_id}.md"
        
        # 加载模板
        template_file = "/workspace/projects/workspace/data/simulation/plans/TRADE_PLAN_TEMPLATE.md"
        with open(template_file, 'r') as f:
            template = f.read()
        
        # 填充模板
        content = template.format(
            plan_id=plan_id,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="ACTIVE",
            symbol=trade['symbol'],
            action=trade['action'],
            quantity=trade['quantity'],
            price=trade['price'],
            amount=trade['amount'],
            trade_time=trade['time'],
            reasoning=reasoning or "待补充",
            technical_analysis="待分析",
            fundamental_analysis="待分析",
            news_analysis="待分析",
            target_price="待设定",
            expected_return="待设定",
            holding_period="待设定",
            stop_loss_price="待设定",
            stop_loss_pct="8",
            max_loss="待计算",
            take_profit_price="待设定",
            take_profit_pct="15",
            max_profit="待计算",
            exit_time="",
            exit_price="",
            actual_pnl="",
            actual_pnl_pct="",
            holding_duration="",
            expected_outcome="",
            actual_outcome="",
            deviation_reason="",
            success_points="",
            improvement_points="",
            lessons_learned="",
            other_pattern="",
            next_action="",
            notes="",
            record_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(plan_file, 'w') as f:
            f.write(content)
    
    def close_position(self, symbol, quantity=None, price=None, reasoning=""):
        """平仓"""
        symbol = symbol.upper()
        
        if symbol not in self.config['positions']:
            print(f"   ❌ 未持有 {symbol}")
            return None
        
        pos = self.config['positions'][symbol]
        
        if quantity is None or quantity >= pos['quantity']:
            quantity = pos['quantity']
        
        if price is None:
            # 获取当前价格
            quote = self.finnhub.get_quote(symbol)
            price = quote.get('current', pos['current_price'])
        
        return self.execute_trade(symbol, 'SELL', quantity, price, reasoning)
    
    def get_portfolio_summary(self):
        """获取持仓摘要"""
        total_value = self.config['cash']
        total_cost = 0
        total_pnl = 0
        
        positions_summary = []
        
        for symbol, pos in self.config['positions'].items():
            # 获取最新价格
            quote = self.finnhub.get_quote(symbol)
            current_price = quote.get('current', pos['current_price'])
            
            market_value = current_price * pos['quantity']
            cost_value = pos['cost_basis'] * pos['quantity']
            pnl = market_value - cost_value
            pnl_pct = (pnl / cost_value) * 100 if cost_value > 0 else 0
            
            total_value += market_value
            total_cost += cost_value
            total_pnl += pnl
            
            positions_summary.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'cost_basis': pos['cost_basis'],
                'current_price': current_price,
                'market_value': market_value,
            'pnl': pnl,
                'pnl_pct': pnl_pct
            })
        
        return {
            'cash': self.config['cash'],
            'positions_value': total_value - self.config['cash'],
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / self.config['initial_capital']) * 100,
            'positions': positions_summary,
            'position_count': len(positions_summary)
        }
    
    def print_portfolio(self):
        """打印持仓"""
        summary = self.get_portfolio_summary()
        
        print("="*70)
        print("🇺🇸 US_SIM_001 持仓摘要")
        print("="*70)
        print(f"💰 现金: ${summary['cash']:,.2f}")
        print(f"📊 持仓市值: ${summary['positions_value']:,.2f}")
        print(f"💵 总资产: ${summary['total_value']:,.2f}")
        print(f"📈 总盈亏: ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)")
        print(f"📋 持仓数量: {summary['position_count']} 个标的")
        print()
        
        if summary['positions']:
            print("📊 持仓明细:")
            for pos in summary['positions']:
                emoji = "🟢" if pos['pnl'] > 0 else "🔴"
                print(f"   {emoji} {pos['symbol']}: {pos['quantity']}股 | "
                      f"成本:${pos['cost_basis']:.2f} | 现价:${pos['current_price']:.2f} | "
                      f"盈亏:${pos['pnl']:,.2f} ({pos['pnl_pct']:+.2f}%)")
        
        print("="*70)
    
    def generate_experiment_report(self):
        """生成实验报告"""
        trades = self.config['trades']
        
        if not trades:
            print("暂无交易记录")
            return
        
        winning_trades = [t for t in trades if t.get('realized_pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('realized_pnl', 0) <= 0]
        
        total_pnl = sum(t.get('realized_pnl', 0) for t in trades)
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        avg_win = sum(t['realized_pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['realized_pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = abs(sum(t['realized_pnl'] for t in winning_trades) / sum(t['realized_pnl'] for t in losing_trades)) if losing_trades and sum(t['realized_pnl'] for t in losing_trades) != 0 else 0
        
        print("="*70)
        print("📊 US_SIM_001 实验交易报告")
        print("="*70)
        print(f"总交易次数: {len(trades)}")
        print(f"盈利次数: {len(winning_trades)}")
        print(f"亏损次数: {len(losing_trades)}")
        print(f"胜率: {win_rate:.2f}%")
        print(f"总盈亏: ${total_pnl:,.2f}")
        print(f"平均盈利: ${avg_win:,.2f}")
        print(f"平均亏损: ${avg_loss:,.2f}")
        print(f"盈亏比: {profit_factor:.2f}")
        print("="*70)
    
    def quick_trade(self, symbol, action, amount_usd, reasoning=""):
        """快速交易 (按金额)"""
        symbol = symbol.upper()
        
        # 获取当前价格
        quote = self.finnhub.get_quote(symbol)
        price = quote.get('current')
        
        if not price:
            print(f"   ❌ 无法获取 {symbol} 价格")
            return None
        
        # 计算数量
        quantity = int(amount_usd / price)
        
        if quantity < 1:
            print(f"   ❌ 金额不足购买1股 {symbol} (当前价 ${price:.2f})")
            return None
        
        return self.execute_trade(symbol, action, quantity, price, reasoning)


# 快捷函数
def add_symbols(symbols):
    """添加标的到关注列表"""
    trader = USSim001AggressiveTrader()
    trader.add_to_watchlist(symbols)
    trader.save_config()


def buy(symbol, quantity=None, amount=None, reasoning=""):
    """买入"""
    trader = USSim001AggressiveTrader()
    
    if amount:
        return trader.quick_trade(symbol, 'BUY', amount, reasoning)
    elif quantity:
        quote = trader.finnhub.get_quote(symbol)
        price = quote.get('current', 0)
        return trader.execute_trade(symbol, 'BUY', quantity, price, reasoning)


def sell(symbol, quantity=None, reasoning=""):
    """卖出"""
    trader = USSim001AggressiveTrader()
    return trader.close_position(symbol, quantity, reasoning=reasoning)


def portfolio():
    """查看持仓"""
    trader = USSim001AggressiveTrader()
    trader.print_portfolio()


def report():
    """查看交易报告"""
    trader = USSim001AggressiveTrader()
    trader.generate_experiment_report()


if __name__ == '__main__':
    print("="*70)
    print("🇺🇸 US_SIM_001 激进交易实验系统 v2.0")
    print("="*70)
    print()
    print("Chief指导: 放开标的限制，大胆试错，全面记录，不断修正")
    print()
    
    trader = USSim001AggressiveTrader()
    
    # 显示当前状态
    trader.print_portfolio()
    
    print()
    print("💡 可用操作:")
    print("   add_symbols(['INTC', 'WDC'])  - 添加标的")
    print("   buy('INTC', amount=10000)     - 买入$10,000的Intel")
    print("   sell('NVDA', quantity=50)     - 卖出50股NVDA")
    print("   portfolio()                    - 查看持仓")
    print("   report()                       - 查看交易报告")
