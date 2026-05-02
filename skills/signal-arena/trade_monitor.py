#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena - A股模拟交易监控器 (v2.4)
模拟盘A股交易，用于生成训练数据
即时重试监控，失败后自动连续重试最多3次
"""

import json
import logging
import random
import sys
import time
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

# A股热门股票池 (模拟用)
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

class AShareTradeSimulator:
    """A股模拟交易器 (v2.4)"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / "a_portfolio.json"
        self.trades_file = self.data_dir / "a_trades.json"
        self.signals_file = self.data_dir / "a_signals.json"
        self.status_file = self.data_dir / "trade_status.json"
        
        self.portfolio = self._load_portfolio()
        self.trades = self._load_trades()
        
    def _load_portfolio(self) -> Dict:
        """加载持仓"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "cash": 1000000.0,  # 初始资金100万人民币
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
    
    def _save_status(self, status: str, message: str, retry_count: int = 0):
        """保存交易状态"""
        status_data = {
            "status": status,
            "message": message,
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
    
    def _is_a_trading_hours(self) -> bool:
        """检查是否为A股交易时间"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周末休市
        if weekday >= 5:
            return False
            
        # A股节假日（简化处理）
        if self._is_a_holiday(now):
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
    
    def _is_a_holiday(self, date: datetime) -> bool:
        """检查是否为A股节假日 (简化版)"""
        # 五一劳动节 (5月1日-5月5日放假，但5月1日是节日当天)
        if date.month == 5 and date.day == 1:
            return True
        # 元旦
        if date.month == 1 and date.day == 1:
            return True
        # 国庆
        if date.month == 10 and date.day >= 1 and date.day <= 7:
            return True
        # 春节（简化，除夕到初六）
        if date.month == 1 and date.day >= 28 and date.day <= 31:
            return True
        if date.month == 2 and date.day >= 1 and date.day <= 3:
            return True
        return False
    
    def _generate_mock_price(self, stock: Dict) -> Dict:
        """生成模拟价格数据"""
        base_price = random.uniform(5, 2000)
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
                logger.info(f"✅ 买入 {name}({symbol}) {quantity}股 @ ¥{price}")
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
                    logger.info(f"✅ 卖出 {name}({symbol}) {quantity}股 @ ¥{price}")
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
    
    def run(self) -> Dict:
        """执行模拟交易"""
        logger.info("=" * 60)
        logger.info("🇨🇳 Signal Arena - A股模拟交易 v2.4 启动")
        logger.info("=" * 60)
        
        now = datetime.now()
        logger.info(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查是否交易日
        if not self._is_a_trading_hours():
            logger.info("⏸️ 当前非A股交易时间，跳过执行")
            logger.info("   A股交易时间: 09:30-11:30, 13:00-15:00")
            if self._is_a_holiday(now):
                logger.info(f"   📢 今日为A股节假日，休市")
            self._save_status("skipped", "非交易时间", 0)
            return {"status": "skipped", "reason": "non_trading_hours"}
        
        logger.info("✅ A股交易时间内，开始分析...")
        
        try:
            # 1. 市场分析 - 生成模拟市场数据
            logger.info("\n📊 1. A股市场分析")
            market_data = []
            for stock in A_STOCKS:
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
            logger.info(f"   现金: ¥{self.portfolio['cash']:,.2f}")
            logger.info(f"   持仓数量: {len(self.portfolio['positions'])}")
            for symbol, pos in self.portfolio["positions"].items():
                logger.info(f"      {pos['name']}({symbol}): {pos['quantity']}股 | 成本:¥{pos['avg_cost']:.2f}")
            logger.info(f"   总市值: ¥{self.portfolio['total_value']:,.2f}")
            
            # 计算收益率
            initial_cash = 1000000.0
            pnl = self.portfolio["total_value"] - initial_cash
            pnl_pct = (pnl / initial_cash) * 100
            logger.info(f"   累计盈亏: ¥{pnl:,.2f} ({pnl_pct:+.2f}%)")
            
            logger.info("\n✅ 模拟盘A股交易执行完成")
            
            result = {
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
            self._save_status("success", "交易执行成功", 0)
            return result
            
        except Exception as e:
            logger.error(f"❌ 交易执行失败: {e}")
            self._save_status("error", str(e), 0)
            return {"status": "error", "reason": str(e)}

def run_with_retry(max_retries: int = 3):
    """带重试机制的执行器"""
    simulator = AShareTradeSimulator()
    
    for attempt in range(max_retries + 1):
        logger.info(f"\n🚀 执行尝试 {attempt + 1}/{max_retries + 1}")
        
        result = simulator.run()
        
        if result["status"] == "success":
            logger.info(f"✅ 执行成功（尝试 {attempt + 1}）")
            return result
        
        if result["status"] == "skipped":
            logger.info("⏸️ 非交易时间，无需重试")
            return result
        
        # 失败且还有重试机会
        if attempt < max_retries:
            wait_time = 5 if attempt == 0 else 10
            logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
        else:
            logger.error(f"❌ 已达到最大重试次数({max_retries})，本次执行失败")
    
    return result

def main():
    """主函数 - 即时重试监控模式"""
    logger.info("\n" + "=" * 60)
    logger.info("🌅 模拟盘A股交易 - v2.4 即时重试监控系统")
    logger.info("=" * 60)
    
    result = run_with_retry(max_retries=3)
    
    # 输出JSON结果（供调用方解析）
    print("\n" + "=" * 60)
    print("RESULT_JSON:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    main()
