#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena - 港股模拟交易运行器
模拟盘港股交易，用于生成训练数据
"""

import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 港股热门股票池 (模拟用)
HK_STOCKS = [
    {"symbol": "00700", "name": "腾讯控股", "sector": "科技"},
    {"symbol": "09988", "name": "阿里巴巴-SW", "sector": "科技"},
    {"symbol": "03690", "name": "美团-W", "sector": "科技"},
    {"symbol": "01810", "name": "小米集团-W", "sector": "科技"},
    {"symbol": "00981", "name": "中芯国际", "sector": "科技"},
    {"symbol": "01299", "name": "友邦保险", "sector": "金融"},
    {"symbol": "02318", "name": "中国平安", "sector": "金融"},
    {"symbol": "03988", "name": "中国银行", "sector": "金融"},
    {"symbol": "00005", "name": "汇丰控股", "sector": "金融"},
    {"symbol": "00883", "name": "中国海洋石油", "sector": "能源"},
    {"symbol": "00857", "name": "中国石油股份", "sector": "能源"},
    {"symbol": "00386", "name": "中国石油化工", "sector": "能源"},
    {"symbol": "02331", "name": "李宁", "sector": "消费"},
    {"symbol": "02020", "name": "安踏体育", "sector": "消费"},
    {"symbol": "06186", "name": "中国飞鹤", "sector": "消费"},
    {"symbol": "02269", "name": "药明生物", "sector": "医药"},
    {"symbol": "01093", "name": "石药集团", "sector": "医药"},
    {"symbol": "02359", "name": "药明康德", "sector": "医药"},
    {"symbol": "09618", "name": "京东集团-SW", "sector": "电商"},
    {"symbol": "09888", "name": "百度集团-SW", "sector": "科技"},
]

class HKTradeSimulator:
    """港股模拟交易器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.trades_file = self.data_dir / "trades.json"
        self.signals_file = self.data_dir / "signals.json"
        
        self.portfolio = self._load_portfolio()
        self.trades = self._load_trades()
        
    def _load_portfolio(self) -> Dict:
        """加载持仓"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "cash": 1000000.0,  # 初始资金100万港币
            "positions": {},
            "total_value": 1000000.0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_trades(self) -> List:
        """加载交易记录"""
        if self.trades_file.exists():
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_portfolio(self):
        """保存持仓"""
        self.portfolio["last_updated"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        """保存交易记录"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def _is_hk_trading_hours(self) -> bool:
        """检查是否为港股交易时间"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周末休市
        if weekday >= 5:
            return False
            
        # 香港节假日（简化处理）
        if self._is_hk_holiday(now):
            return False
        
        hour = now.hour
        minute = now.minute
        time_val = hour * 100 + minute
        
        # 港股交易时间
        # 开市前: 900-930 (竞价)
        # 早市: 930-1200
        # 午市: 1300-1600
        if 930 <= time_val < 1200 or 1300 <= time_val < 1600:
            return True
        return False
    
    def _is_hk_holiday(self, date: datetime) -> bool:
        """检查是否为香港节假日 (简化版)"""
        # 五一劳动节
        if date.month == 5 and date.day == 1:
            return True
        # 元旦
        if date.month == 1 and date.day == 1:
            return True
        # 国庆
        if date.month == 10 and date.day == 1:
            return True
        # 春节（简化，仅检查正月初一）
        if date.month == 1 and date.day <= 3:
            return True
        return False
    
    def _generate_mock_price(self, stock: Dict) -> Dict:
        """生成模拟价格数据"""
        base_price = random.uniform(10, 500)
        change_pct = random.uniform(-0.05, 0.05)
        price = base_price * (1 + change_pct)
        
        return {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "price": round(price, 2),
            "open": round(base_price * random.uniform(0.98, 1.02), 2),
            "high": round(price * random.uniform(1.0, 1.03), 2),
            "low": round(price * random.uniform(0.97, 1.0), 2),
            "prev_close": round(base_price, 2),
            "change": round(price - base_price, 2),
            "change_pct": round(change_pct * 100, 2),
            "volume": random.randint(100000, 10000000),
            "turnover": round(price * random.randint(100000, 10000000) / 100000000, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_stock(self, stock_data: Dict) -> Dict:
        """分析股票并生成信号"""
        change_pct = stock_data["change_pct"]
        volume = stock_data["volume"]
        
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
            "symbol": stock_data["symbol"],
            "name": stock_data["name"],
            "signal": signal,
            "score": max(0, min(100, score)),
            "confidence": round(confidence, 2),
            "current_price": stock_data["price"],
            "change_pct": change_pct,
            "recommendation": self._get_recommendation(signal, score),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recommendation(self, signal: str, score: int) -> str:
        """获取推荐建议"""
        if signal in ["STRONG_BUY", "BUY"] and score >= 60:
            return "建议买入"
        elif signal == "WEAK_BUY" and score >= 55:
            return "可以关注"
        elif signal in ["STRONG_SELL", "SELL"] and score <= 40:
            return "建议卖出"
        elif signal == "WEAK_SELL" and score <= 45:
            return "谨慎持有"
        return "观望"
    
    def _execute_trade(self, signal: Dict, action: str, quantity: int = 100):
        """执行交易"""
        price = signal["current_price"]
        symbol = signal["symbol"]
        name = signal["name"]
        
        if action == "BUY":
            cost = price * quantity * 1.001  # 含0.1%手续费
            if self.portfolio["cash"] >= cost:
                self.portfolio["cash"] -= cost
                if symbol not in self.portfolio["positions"]:
                    self.portfolio["positions"][symbol] = {
                        "name": name,
                        "quantity": 0,
                        "avg_cost": 0
                    }
                pos = self.portfolio["positions"][symbol]
                total_cost = pos["avg_cost"] * pos["quantity"] + cost
                pos["quantity"] += quantity
                pos["avg_cost"] = total_cost / pos["quantity"] if pos["quantity"] > 0 else 0
                
                trade = {
                    "action": "BUY",
                    "symbol": symbol,
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "cost": round(cost, 2),
                    "timestamp": datetime.now().isoformat(),
                    "reason": signal.get("recommendation", "")
                }
                self.trades.append(trade)
                logger.info(f"✅ 买入 {name}({symbol}) {quantity}股 @ ${price}")
                return True
            else:
                logger.warning(f"❌ 资金不足，无法买入 {name}")
                return False
                
        elif action == "SELL":
            if symbol in self.portfolio["positions"]:
                pos = self.portfolio["positions"][symbol]
                if pos["quantity"] >= quantity:
                    revenue = price * quantity * 0.999  # 含0.1%手续费
                    self.portfolio["cash"] += revenue
                    pos["quantity"] -= quantity
                    if pos["quantity"] == 0:
                        del self.portfolio["positions"][symbol]
                    
                    trade = {
                        "action": "SELL",
                        "symbol": symbol,
                        "name": name,
                        "quantity": quantity,
                        "price": price,
                        "revenue": round(revenue, 2),
                        "timestamp": datetime.now().isoformat(),
                        "reason": signal.get("recommendation", "")
                    }
                    self.trades.append(trade)
                    logger.info(f"✅ 卖出 {name}({symbol}) {quantity}股 @ ${price}")
                    return True
            logger.warning(f"❌ 持仓不足，无法卖出 {name}")
            return False
        
        return False
    
    def _update_portfolio_value(self, market_data: List[Dict]):
        """更新账户总市值"""
        positions_value = 0
        price_map = {d["symbol"]: d["price"] for d in market_data}
        
        for symbol, pos in self.portfolio["positions"].items():
            if symbol in price_map:
                positions_value += price_map[symbol] * pos["quantity"]
        
        self.portfolio["total_value"] = self.portfolio["cash"] + positions_value
    
    def run(self):
        """执行模拟交易"""
        logger.info("=" * 50)
        logger.info("🌏 Signal Arena - 港股模拟交易启动")
        logger.info("=" * 50)
        
        now = datetime.now()
        logger.info(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查是否交易日
        if not self._is_hk_trading_hours():
            logger.info("⏸️ 当前非港股交易时间，跳过执行")
            logger.info("   港股交易时间: 09:30-12:00, 13:00-16:00")
            if self._is_hk_holiday(now):
                logger.info(f"   📢 今日为香港节假日，休市")
            return {"status": "skipped", "reason": "non_trading_hours"}
        
        logger.info("✅ 港股交易时间内，开始分析...")
        
        # 1. 市场分析 - 生成模拟市场数据
        logger.info("\n📊 1. 港股市场分析")
        market_data = []
        for stock in HK_STOCKS:
            data = self._generate_mock_price(stock)
            market_data.append(data)
        
        # 计算市场概况
        advancers = sum(1 for d in market_data if d["change_pct"] > 0)
        decliners = sum(1 for d in market_data if d["change_pct"] < 0)
        avg_change = sum(d["change_pct"] for d in market_data) / len(market_data)
        
        logger.info(f"   上涨: {advancers}只 | 下跌: {decliners}只 | 平均涨跌幅: {avg_change:.2f}%")
        
        # 2. 选股与评分
        logger.info("\n🎯 2. 选股与评分")
        signals = []
        for data in market_data:
            signal = self._analyze_stock(data)
            signals.append(signal)
            if signal["score"] >= 60 or signal["score"] <= 40:
                logger.info(f"   {data['name']}({data['symbol']}): 评分{signal['score']} | 信号:{signal['signal']} | {signal['recommendation']}")
        
        # 保存信号
        with open(self.signals_file, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        # 3. 执行买卖
        logger.info("\n💰 3. 执行交易")
        
        # 买入高分股票
        buy_signals = sorted([s for s in signals if s["score"] >= 65], 
                            key=lambda x: x["score"], reverse=True)[:3]
        for signal in buy_signals:
            self._execute_trade(signal, "BUY", quantity=random.choice([100, 200, 500]))
        
        # 卖出低分持仓
        sell_signals = sorted([s for s in signals if s["score"] <= 35], 
                             key=lambda x: x["score"])[:3]
        for signal in sell_signals:
            if signal["symbol"] in self.portfolio["positions"]:
                self._execute_trade(signal, "SELL", quantity=random.choice([100, 200]))
        
        # 4. 更新持仓价值并保存
        self._update_portfolio_value(market_data)
        self._save_portfolio()
        self._save_trades()
        
        # 5. 记录交易数据
        logger.info("\n📈 4. 账户概况")
        logger.info(f"   现金: ${self.portfolio['cash']:,.2f}")
        logger.info(f"   持仓数量: {len(self.portfolio['positions'])}")
        for symbol, pos in self.portfolio["positions"].items():
            logger.info(f"      {pos['name']}({symbol}): {pos['quantity']}股 | 成本:${pos['avg_cost']:.2f}")
        logger.info(f"   总市值: ${self.portfolio['total_value']:,.2f}")
        
        # 计算收益率
        initial_cash = 1000000.0
        pnl = self.portfolio["total_value"] - initial_cash
        pnl_pct = (pnl / initial_cash) * 100
        logger.info(f"   累计盈亏: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        logger.info("\n✅ 模拟盘港股交易执行完成")
        
        return {
            "status": "success",
            "timestamp": now.isoformat(),
            "signals_count": len(signals),
            "trades_count": len(self.trades),
            "portfolio": {
                "cash": round(self.portfolio["cash"], 2),
                "positions_count": len(self.portfolio["positions"]),
                "total_value": round(self.portfolio["total_value"], 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2)
            }
        }

def main():
    """主函数"""
    simulator = HKTradeSimulator()
    result = simulator.run()
    
    # 输出JSON结果（供调用方解析）
    print("\n" + "=" * 50)
    print("RESULT_JSON:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    main()
