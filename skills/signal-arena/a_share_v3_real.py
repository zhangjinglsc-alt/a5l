#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena - A股模拟交易监控器 (v3.0)
修复版：接入AKShare真实数据源
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import akshare as ak

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class RealPriceDataSource:
    """真实价格数据源"""
    
    @staticmethod
    def get_a_stock_price(symbol: str) -> Dict:
        """获取A股真实价格"""
        try:
            # 使用AKShare获取实时行情
            spot_df = ak.stock_zh_a_spot_em()
            stock_data = spot_df[spot_df["代码"] == symbol]
            
            if not stock_data.empty:
                return {
                    "symbol": symbol,
                    "price": float(stock_data["最新价"].values[0]),
                    "open": float(stock_data["开盘价"].values[0]),
                    "high": float(stock_data["最高价"].values[0]),
                    "low": float(stock_data["最低价"].values[0]),
                    "prev_close": float(stock_data["昨收"].values[0]),
                    "volume": int(stock_data["成交量"].values[0]),
                    "change_pct": float(stock_data["涨跌幅"].values[0]),
                    "source": "akshare_real"
                }
        except Exception as e:
            logger.error(f"获取{symbol}价格失败: {e}")
        return None
    
    @staticmethod
    def get_hk_stock_price(symbol: str) -> Dict:
        """获取港股真实价格"""
        try:
            # 使用AKShare获取港股实时行情
            hk_spot = ak.stock_hk_spot_em()
            stock_data = hk_spot[hk_spot["代码"] == symbol]
            
            if not stock_data.empty:
                return {
                    "symbol": symbol,
                    "price": float(stock_data["最新价"].values[0]),
                    "open": float(stock_data["开盘价"].values[0]),
                    "high": float(stock_data["最高价"].values[0]),
                    "low": float(stock_data["最低价"].values[0]),
                    "prev_close": float(stock_data["昨收"].values[0]),
                    "volume": int(stock_data["成交量"].values[0]) if "成交量" in stock_data.columns else 0,
                    "change_pct": float(stock_data["涨跌幅"].values[0]) if "涨跌幅" in stock_data.columns else 0,
                    "source": "akshare_real"
                }
        except Exception as e:
            logger.error(f"获取港股{symbol}价格失败: {e}")
        return None


class AShareTradeSimulatorV3:
    """A股模拟交易器 v3.0 - 真实数据版"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / "a_portfolio.json"
        self.trades_file = self.data_dir / "a_trades.json"
        
        self.portfolio = self._load_portfolio()
        self.trades = self._load_trades()
        self.price_source = RealPriceDataSource()
        
    def _load_portfolio(self) -> Dict:
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "cash": 5000000.0,  # 初始资金500万人民币
            "positions": {},
            "total_value": 5000000.0,
            "last_updated": datetime.now().isoformat(),
            "version": "3.0_real_data"
        }
    
    def _load_trades(self) -> List:
        if self.trades_file.exists():
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_portfolio(self):
        self.portfolio["last_updated"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def execute_trade(self, symbol: str, action: str, quantity: int) -> bool:
        """执行交易"""
        price_data = self.price_source.get_a_stock_price(symbol)
        if not price_data:
            logger.error(f"无法获取{symbol}价格，交易取消")
            return False
        
        price = price_data["price"]
        amount = price * quantity
        commission = amount * 0.0003  # 手续费0.03%
        
        if action == "BUY":
            total_cost = amount + commission
            if self.portfolio["cash"] < total_cost:
                logger.warning(f"资金不足，无法买入{symbol}")
                return False
            
            # 更新持仓
            if symbol not in self.portfolio["positions"]:
                self.portfolio["positions"][symbol] = {
                    "quantity": 0, "avg_cost": 0
                }
            
            pos = self.portfolio["positions"][symbol]
            total_quantity = pos["quantity"] + quantity
            total_cost_basis = pos["quantity"] * pos["avg_cost"] + amount
            pos["quantity"] = total_quantity
            pos["avg_cost"] = total_cost_basis / total_quantity if total_quantity > 0 else 0
            
            self.portfolio["cash"] -= total_cost
            
        elif action == "SELL":
            if symbol not in self.portfolio["positions"] or self.portfolio["positions"][symbol]["quantity"] < quantity:
                logger.warning(f"持仓不足，无法卖出{symbol}")
                return False
            
            revenue = amount - commission
            self.portfolio["positions"][symbol]["quantity"] -= quantity
            self.portfolio["cash"] += revenue
            
            if self.portfolio["positions"][symbol]["quantity"] == 0:
                del self.portfolio["positions"][symbol]
        
        # 记录交易
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "source": "real_data"
        }
        self.trades.append(trade)
        
        self._save_portfolio()
        self._save_trades()
        
        logger.info(f"{action} {symbol} {quantity}股 @ {price}")
        return True


# A股热门股票池 (同v2.4)
A_STOCKS = [
    {"symbol": "000001", "name": "平安银行", "sector": "金融"},
    {"symbol": "000002", "name": "万科A", "sector": "地产"},
    {"symbol": "000858", "name": "五粮液", "sector": "消费"},
    {"symbol": "000725", "name": "京东方A", "sector": "科技"},
    {"symbol": "002594", "name": "比亚迪", "sector": "汽车"},
    {"symbol": "002415", "name": "海康威视", "sector": "科技"},
    {"symbol": "002714", "name": "牧原股份", "sector": "农业"},
    {"symbol": "002230", "name": "科大讯飞", "sector": "科技"},
    {"symbol": "300750", "name": "宁德时代", "sector": "新能源"},
    {"symbol": "300059", "name": "东方财富", "sector": "金融"},
    {"symbol": "300124", "name": "汇川技术", "sector": "工业"},
    {"symbol": "600036", "name": "招商银行", "sector": "金融"},
    {"symbol": "600519", "name": "贵州茅台", "sector": "消费"},
    {"symbol": "600276", "name": "恒瑞医药", "sector": "医药"},
    {"symbol": "601318", "name": "中国平安", "sector": "金融"},
    {"symbol": "601012", "name": "隆基绿能", "sector": "新能源"},
    {"symbol": "601888", "name": "中国中免", "sector": "消费"},
    {"symbol": "603259", "name": "药明康德", "sector": "医药"},
    {"symbol": "600900", "name": "长江电力", "sector": "公用"},
    {"symbol": "601166", "name": "兴业银行", "sector": "金融"},
]

def _analyze_stock(price_data: Dict) -> Dict:
    """分析股票并生成信号"""
    change_pct = price_data["change_pct"]
    volume = price_data["volume"]
    
    # 简单评分系统
    score = 50  # 基础分
    signal = "HOLD"
    
    # 价格动量
    if change_pct > 2:
        score += 15
        signal = "BUY"
    elif change_pct > 0.5:
        score += 5
        signal = "WEAK_BUY"
    elif change_pct < -2:
        score -= 15
        signal = "SELL"
    elif change_pct < -0.5:
        score -= 5
        signal = "WEAK_SELL"
    
    # 量能分析
    if volume > 5000000:
        score += 5
    
    # 信号强度
    confidence = min(0.95, max(0.3, abs(score - 50) / 50 + 0.3))
    
    return {
        "symbol": price_data["symbol"],
        "signal": signal,
        "score": max(0, min(100, score)),
        "confidence": round(confidence, 2),
        "current_price": price_data["price"],
        "change_pct": change_pct,
        "timestamp": datetime.now().isoformat()
    }

def _is_a_trading_hours() -> bool:
    """检查是否为A股交易时间"""
    now = datetime.now()
    weekday = now.weekday()
    
    # 周末休市
    if weekday >= 5:
        return False
    
    hour = now.hour
    minute = now.minute
    time_val = hour * 100 + minute
    
    # A股交易时间
    # 早盘: 0930-1130
    # 午盘: 1300-1500
    if 930 <= time_val < 1130 or 1300 <= time_val < 1500:
        return True
    return False

if __name__ == "__main__":
    import random
    simulator = AShareTradeSimulatorV3()
    print("="*60)
    print("🇨🇳 A股模拟交易器 v3.0 已启动（真实数据源）")
    print("="*60)
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前现金: ¥{simulator.portfolio['cash']:,.2f}")
    print(f"持仓数量: {len(simulator.portfolio['positions'])}")
    
    # 检查交易时间
    if not _is_a_trading_hours():
        print("⏸️ 当前非A股交易时间，跳过执行")
        print("   A股交易时间: 09:30-11:30, 13:00-15:00")
        exit(0)
    
    print("\n📊 1. 获取A股实时行情（AKShare数据源）")
    market_data = []
    for stock in A_STOCKS:
        price_data = simulator.price_source.get_a_stock_price(stock["symbol"])
        if price_data:
            price_data["name"] = stock["name"]
            market_data.append(price_data)
            print(f"   {stock['name']}({stock['symbol']}): ¥{price_data['price']:.2f} | {price_data['change_pct']:+.2f}%")
    
    if not market_data:
        print("❌ 获取行情失败，交易取消")
        exit(1)
    
    # 计算市场概况
    advancers = sum(1 for d in market_data if d["change_pct"] > 0)
    decliners = sum(1 for d in market_data if d["change_pct"] < 0)
    avg_change = sum(d["change_pct"] for d in market_data) / len(market_data)
    print(f"\n📈 市场概况: 上涨{advancers}只 | 下跌{decliners}只 | 平均涨跌幅: {avg_change:+.2f}%")
    
    print("\n🎯 2. 选股与信号分析")
    signals = []
    for data in market_data:
        signal = _analyze_stock(data)
        signals.append(signal)
        if signal["score"] >= 60 or signal["score"] <= 40:
            print(f"   {data['name']}({data['symbol']}): 评分{signal['score']} | 信号:{signal['signal']}")
    
    print("\n💰 3. 执行交易")
    # 买入高分股票（前3名）
    buy_signals = sorted([s for s in signals if s["score"] >= 65], key=lambda x: x["score"], reverse=True)[:3]
    for signal in buy_signals:
        stock = next(s for s in A_STOCKS if s["symbol"] == signal["symbol"])
        quantity = random.choice([100, 200, 500])
        success = simulator.execute_trade(signal["symbol"], "BUY", quantity)
        if success:
            print(f"✅ 买入 {stock['name']}({signal['symbol']}) {quantity}股 @ ¥{signal['current_price']:.2f}")
    
    # 卖出低分持仓（前3名）
    sell_signals = sorted([s for s in signals if s["score"] <= 35 and s["symbol"] in simulator.portfolio["positions"]], key=lambda x: x["score"])[:3]
    for signal in sell_signals:
        stock = next(s for s in A_STOCKS if s["symbol"] == signal["symbol"])
        quantity = random.choice([100, 200])
        success = simulator.execute_trade(signal["symbol"], "SELL", quantity)
        if success:
            print(f"✅ 卖出 {stock['name']}({signal['symbol']}) {quantity}股 @ ¥{signal['current_price']:.2f}")
    
    # 计算总市值
    total_value = simulator.portfolio["cash"]
    price_map = {d["symbol"]: d["price"] for d in market_data}
    for symbol, pos in simulator.portfolio["positions"].items():
        if symbol in price_map:
            total_value += price_map[symbol] * pos["quantity"]
    
    print("\n📊 4. 账户更新")
    print(f"   现金: ¥{simulator.portfolio['cash']:,.2f}")
    print(f"   持仓数量: {len(simulator.portfolio['positions'])}")
    for symbol, pos in simulator.portfolio["positions"].items():
        stock_name = next(s["name"] for s in A_STOCKS if s["symbol"] == symbol)
        current_price = price_map.get(symbol, pos["avg_cost"])
        profit = (current_price - pos["avg_cost"]) * pos["quantity"]
        profit_pct = (profit / (pos["avg_cost"] * pos["quantity"])) * 100 if pos["avg_cost"] > 0 else 0
        print(f"      {stock_name}({symbol}): {pos['quantity']}股 | 成本¥{pos['avg_cost']:.2f} | 当前¥{current_price:.2f} | 盈亏¥{profit:,.2f} ({profit_pct:+.2f}%)")
    print(f"   总市值: ¥{total_value:,.2f}")
    initial_cash = 5000000.0
    pnl = total_value - initial_cash
    pnl_pct = (pnl / initial_cash) * 100
    print(f"   累计盈亏: ¥{pnl:,.2f} ({pnl_pct:+.2f}%)")
    
    print("\n✅ A股模拟交易 v3.0 执行完成！")
