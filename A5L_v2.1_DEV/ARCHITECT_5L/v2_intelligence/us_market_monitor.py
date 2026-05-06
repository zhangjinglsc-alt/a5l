#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L v2.0 美股实时监控系统
为今晚21:30美股开盘准备

功能:
1. 实时行情监控 (AAPL/NVDA/TSLA)
2. 模拟账户追踪
3. 自动告警
4. 飞书推送
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StockQuote:
    """股票报价"""
    symbol: str
    price: float
    change: float
    change_pct: float
    volume: int
    timestamp: str
    
    @property
    def is_rising(self) -> bool:
        return self.change > 0
    
    @property
    def is_falling(self) -> bool:
        return self.change < 0


@dataclass
class Position:
    """持仓"""
    symbol: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_cost) * self.shares
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.avg_cost == 0:
            return 0
        return (self.current_price - self.avg_cost) / self.avg_cost


class USMarketMonitor:
    """
    美股实时监控系统
    
    监控标的:
    - AAPL (苹果)
    - NVDA (英伟达)
    - TSLA (特斯拉)
    """
    
    MONITORING_STOCKS = ["AAPL", "NVDA", "TSLA"]
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.quotes: Dict[str, StockQuote] = {}
        self.is_market_open = False
        self.alert_threshold = 0.05  # 5%告警
        
        # 模拟账户初始化
        self._init_simulated_account()
        
        logger.info("📈 US Market Monitor initialized")
    
    def _init_simulated_account(self):
        """初始化模拟账户"""
        # US_SIM_001 模拟持仓
        self.positions = {
            "AAPL": Position(symbol="AAPL", shares=10, avg_cost=180.50),
            "NVDA": Position(symbol="NVDA", shares=5, avg_cost=890.00),
            "TSLA": Position(symbol="TSLA", shares=8, avg_cost=175.30)
        }
        
        logger.info("💰 Simulated account initialized")
        for symbol, pos in self.positions.items():
            logger.info(f"   {symbol}: {pos.shares} shares @ ${pos.avg_cost:.2f}")
    
    async def start_monitoring(self):
        """开始监控"""
        logger.info("🔴 Starting US market monitoring...")
        self.is_market_open = True
        
        # 创建监控任务
        tasks = [
            self._monitor_quotes(),
            self._monitor_positions(),
            self._check_alerts()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _monitor_quotes(self):
        """监控行情"""
        while self.is_market_open:
            for symbol in self.MONITORING_STOCKS:
                try:
                    quote = await self._fetch_quote(symbol)
                    self.quotes[symbol] = quote
                    
                    # 更新持仓价格
                    if symbol in self.positions:
                        self.positions[symbol].current_price = quote.price
                    
                    logger.info(f"📊 {symbol}: ${quote.price:.2f} ({quote.change_pct:+.2f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Error fetching {symbol}: {e}")
            
            # 每5秒刷新一次
            await asyncio.sleep(5)
    
    async def _fetch_quote(self, symbol: str) -> StockQuote:
        """获取实时报价 (模拟)"""
        import random
        
        # 模拟价格变动
        base_prices = {"AAPL": 180.50, "NVDA": 890.00, "TSLA": 175.30}
        base = base_prices.get(symbol, 100)
        
        # 随机波动 -2% ~ +2%
        change_pct = random.uniform(-0.02, 0.02)
        price = base * (1 + change_pct)
        change = price - base
        
        return StockQuote(
            symbol=symbol,
            price=price,
            change=change,
            change_pct=change_pct * 100,
            volume=random.randint(1000000, 10000000),
            timestamp=datetime.now().isoformat()
        )
    
    async def _monitor_positions(self):
        """监控持仓"""
        while self.is_market_open:
            await asyncio.sleep(30)  # 每30秒检查一次持仓
            
            total_pnl = 0
            total_value = 0
            
            logger.info("\n💼 Position Summary:")
            for symbol, pos in self.positions.items():
                if pos.current_price > 0:
                    pnl = pos.unrealized_pnl
                    pnl_pct = pos.unrealized_pnl_pct * 100
                    value = pos.market_value
                    
                    total_pnl += pnl
                    total_value += value
                    
                    emoji = "🟢" if pnl > 0 else "🔴"
                    logger.info(f"   {emoji} {symbol}: ${value:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            
            logger.info(f"   Total Value: ${total_value:.2f} | Total P&L: ${total_pnl:+.2f}\n")
    
    async def _check_alerts(self):
        """检查告警条件"""
        while self.is_market_open:
            await asyncio.sleep(10)  # 每10秒检查一次
            
            for symbol, pos in self.positions.items():
                pnl_pct = pos.unrealized_pnl_pct
                
                # 亏损超5%告警
                if pnl_pct < -self.alert_threshold:
                    await self._send_alert(symbol, "loss", pnl_pct)
                
                # 盈利超10%提示
                if pnl_pct > 0.10:
                    await self._send_alert(symbol, "profit", pnl_pct)
    
    async def _send_alert(self, symbol: str, alert_type: str, pnl_pct: float):
        """发送告警"""
        emoji = "🚨" if alert_type == "loss" else "🎉"
        logger.warning(f"{emoji} ALERT: {symbol} {alert_type.upper()} {pnl_pct*100:+.2f}%")
        
        # TODO: 发送到飞书
        # await self._notify_feishu(symbol, alert_type, pnl_pct)
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合摘要"""
        total_value = sum(pos.market_value for pos in self.positions.values())
        total_cost = sum(pos.shares * pos.avg_cost for pos in self.positions.values())
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "positions": [
                {
                    "symbol": pos.symbol,
                    "shares": pos.shares,
                    "avg_cost": pos.avg_cost,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_pct": pos.unrealized_pnl_pct * 100
                }
                for pos in self.positions.values()
            ]
        }
    
    async def stop(self):
        """停止监控"""
        self.is_market_open = False
        logger.info("🛑 US Market Monitor stopped")


async def main():
    """主函数 - 美股监控"""
    print("=" * 80)
    print("📈 A5L v2.0 US Market Real-time Monitor")
    print("=" * 80)
    print()
    print("Account: US_SIM_001")
    print("Monitoring: AAPL, NVDA, TSLA")
    print("Market Hours: 21:30-04:00 (Next Day) CST")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    monitor = USMarketMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        await monitor.stop()
        
        # 打印最终摘要
        summary = monitor.get_portfolio_summary()
        print("\n" + "=" * 80)
        print("📊 Final Portfolio Summary")
        print("=" * 80)
        print(f"Total Value: ${summary['total_value']:.2f}")
        print(f"Total P&L: ${summary['total_pnl']:+.2f} ({summary['total_pnl_pct']:+.2f}%)")
        print("\nPositions:")
        for pos in summary['positions']:
            emoji = "🟢" if pos['unrealized_pnl'] > 0 else "🔴"
            print(f"   {emoji} {pos['symbol']}: {pos['shares']} shares | "
                  f"${pos['current_price']:.2f} | P&L: ${pos['unrealized_pnl']:+.2f}")


if __name__ == "__main__":
    asyncio.run(main())
