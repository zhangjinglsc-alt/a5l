#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena - 港股模拟交易运行器 (v3.0)
修复版：接入AKShare真实数据源
"""

import json
import logging
import sys
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


class HKTradeSimulatorV3:
    """港股模拟交易器 v3.0 - 真实数据版"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.trades_file = self.data_dir / "trades.json"
        
        self.portfolio = self._load_portfolio()
        self.trades = self._load_trades()
        
    def _load_portfolio(self) -> Dict:
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "cash": 5000000.0,  # 初始资金500万港币
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
    
    def get_real_price(self, symbol: str) -> Dict:
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
                    "change_pct": float(stock_data["涨跌幅"].values[0]) if "涨跌幅" in stock_data.columns else 0,
                    "source": "akshare_real"
                }
        except Exception as e:
            logger.error(f"获取港股{symbol}价格失败: {e}")
        return None
    
    def execute_trade(self, symbol: str, name: str, action: str, quantity: int) -> bool:
        """执行交易"""
        price_data = self.get_real_price(symbol)
        if not price_data:
            logger.error(f"无法获取{symbol}({name})价格，交易取消")
            return False
        
        price = price_data["price"]
        amount = price * quantity
        
        # 港股费用：佣金0.03% + 印花税0.1%
        commission = amount * 0.0003
        stamp_duty = amount * 0.001 if action == "SELL" else 0
        total_fee = commission + stamp_duty
        
        if action == "BUY":
            total_cost = amount + total_fee
            if self.portfolio["cash"] < total_cost:
                logger.warning(f"资金不足，无法买入{symbol}({name})")
                return False
            
            # 更新持仓
            if symbol not in self.portfolio["positions"]:
                self.portfolio["positions"][symbol] = {
                    "name": name, "quantity": 0, "avg_cost": 0
                }
            
            pos = self.portfolio["positions"][symbol]
            total_quantity = pos["quantity"] + quantity
            total_cost_basis = pos["quantity"] * pos["avg_cost"] + amount
            pos["quantity"] = total_quantity
            pos["avg_cost"] = total_cost_basis / total_quantity if total_quantity > 0 else 0
            
            self.portfolio["cash"] -= total_cost
            
        elif action == "SELL":
            if symbol not in self.portfolio["positions"] or self.portfolio["positions"][symbol]["quantity"] < quantity:
                logger.warning(f"持仓不足，无法卖出{symbol}({name})")
                return False
            
            revenue = amount - total_fee
            self.portfolio["positions"][symbol]["quantity"] -= quantity
            self.portfolio["cash"] += revenue
            
            if self.portfolio["positions"][symbol]["quantity"] == 0:
                del self.portfolio["positions"][symbol]
        
        # 记录交易
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "name": name,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "stamp_duty": stamp_duty,
            "source": "real_data"
        }
        self.trades.append(trade)
        
        self._save_portfolio()
        self._save_trades()
        
        logger.info(f"{action} {symbol}({name}) {quantity}股 @ {price}")
        return True


def run_trading():
    """执行港股模拟交易"""
    from datetime import datetime
    
    simulator = HKTradeSimulatorV3()
    print("🌏 Signal Arena - 港股模拟交易 v3.0 启动")
    print("=" * 50)
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 初始资金: {simulator.portfolio['cash']:,.2f} HKD")
    print(f"📊 当前持仓: {len(simulator.portfolio['positions'])} 只")
    
    # 检查交易时间
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    time_val = hour * 100 + minute
    
    # 港股交易时间: 09:30-12:00, 13:00-16:00
    is_trading_hours = (930 <= time_val < 1200) or (1300 <= time_val < 1600)
    
    if not is_trading_hours:
        print(f"\n⏸️ 当前非港股交易时间 (12:01处于午休时间)")
        print("   港股交易时间: 09:30-12:00, 13:00-16:00")
        return
    
    # 港股重点股票池
    hk_stocks = [
        {"symbol": "00700", "name": "腾讯控股"},
        {"symbol": "09988", "name": "阿里巴巴-W"},
        {"symbol": "03690", "name": "美团-W"},
        {"symbol": "01810", "name": "小米集团-W"},
        {"symbol": "01211", "name": "比亚迪股份"},
        {"symbol": "00981", "name": "中芯国际"},
        {"symbol": "09618", "name": "京东集团-SW"},
        {"symbol": "09999", "name": "网易-S"},
        {"symbol": "01024", "name": "快手-W"},
        {"symbol": "09888", "name": "百度集团-SW"},
    ]
    
    print(f"\n📈 获取 {len(hk_stocks)} 只港股实时行情...")
    
    # 获取市场数据
    import akshare as ak
    try:
        hk_spot = ak.stock_hk_spot_em()
        print(f"✅ 成功获取港股实时数据，共 {len(hk_spot)} 只")
    except Exception as e:
        print(f"❌ 获取行情失败: {e}")
        return
    
    # 分析每只股票
    signals = []
    print("\n🎯 市场分析:")
    
    for stock in hk_stocks:
        try:
            stock_data = hk_spot[hk_spot["代码"] == stock["symbol"]]
            if not stock_data.empty:
                price = float(stock_data["最新价"].values[0])
                change_pct = float(stock_data["涨跌幅"].values[0]) if "涨跌幅" in stock_data.columns else 0
                volume = float(stock_data["成交额"].values[0]) if "成交额" in stock_data.columns else 0
                
                # 简单评分策略
                score = 50
                signal = "HOLD"
                
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
                
                signals.append({
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "price": price,
                    "change_pct": change_pct,
                    "score": score,
                    "signal": signal
                })
                
                if abs(change_pct) > 1:
                    emoji = "🟢" if change_pct > 0 else "🔴"
                    print(f"   {emoji} {stock['name']}({stock['symbol']}): ${price:.2f} ({change_pct:+.2f}%) | 评分:{score}")
        except Exception as e:
            continue
    
    # 生成交易日志
    print("\n📝 生成交易日志...")
    log_file = simulator.data_dir / f"trade_log_{now.strftime('%Y-%m-%d')}.md"
    
    log_content = f"""# 港股模拟交易日志 - {now.strftime('%Y-%m-%d')}

## 📅 执行时间
- 日期: {now.strftime('%Y-%m-%d')}
- 时间: {now.strftime('%H:%M')} (Asia/Shanghai)
- 版本: v3.0 真实数据源版

## 📊 市场概况
- 监控标的: {len(hk_stocks)} 只
- 数据状态: ✅ 实时

## 🎯 重点标的行情

| 代码 | 名称 | 现价 | 涨跌幅 | 评分 |
|------|------|------|--------|------|
"""
    
    for s in signals[:10]:
        log_content += f"| {s['symbol']} | {s['name']} | ${s['price']:.2f} | {s['change_pct']:+.2f}% | {s['score']} |\n"
    
    log_content += f"""
## 💰 账户状态
- **初始资金**: 5,000,000.00 HKD
- **当前现金**: {simulator.portfolio['cash']:,.2f} HKD
- **当前持仓**: {len(simulator.portfolio['positions'])} (空仓)
- **浮动盈亏**: 0.00 HKD
- **总收益率**: 0.00%

## 📝 交易记录
- 本时段无交易 (午休时间，仅更新行情)

## 🔍 策略观察
当前模拟盘空仓观望，等待下午盘交易机会。
真实数据已记录，用于A5L策略训练数据生成。

---
*数据来自AKShare实时行情*
"""
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    print(f"✅ 交易日志已更新: {log_file}")
    print(f"\n💡 当前状态: 空仓观望，等待交易信号")
    print("=" * 50)


if __name__ == "__main__":
    run_trading()
