#!/usr/bin/env python3
"""
CIO策略改进版 - 加入风控和止损
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class ImprovedStrategies:
    """改进版策略库 - 带风控"""
    
    @staticmethod
    def ma_cross_with_stoploss(df: pd.DataFrame, date: str, position: Dict, capital: float,
                                short_window: int = 5, long_window: int = 20,
                                stop_loss: float = 0.05, take_profit: float = 0.10) -> Tuple[str, int]:
        """
        双均线交叉 + 止损止盈
        
        Args:
            stop_loss: 止损比例 (默认5%)
            take_profit: 止盈比例 (默认10%)
        """
        if len(df) < long_window:
            return "HOLD", 0
        
        current_price = df.iloc[-1]['close']
        
        # 检查止损止盈
        if position['shares'] > 0:
            avg_cost = position.get('avg_cost', position.get('cost', 0)) / position['shares']
            if avg_cost > 0:
                pnl_pct = (current_price - avg_cost) / avg_cost
                
                # 止损
                if pnl_pct < -stop_loss:
                    return "SELL", position['shares']
                
                # 止盈
                if pnl_pct > take_profit:
                    return "SELL", position['shares']
        
        # 计算均线
        df = df.copy()
        df['ma_short'] = df['close'].rolling(short_window).mean()
        df['ma_long'] = df['close'].rolling(long_window).mean()
        
        current = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else current
        
        # 金叉买入
        if current['ma_short'] > current['ma_long'] and prev['ma_short'] <= prev['ma_long']:
            if position['shares'] == 0:
                shares = int(capital / current_price / 100) * 100
                return "BUY", shares
        
        # 死叉卖出
        elif current['ma_short'] < current['ma_long'] and prev['ma_short'] >= prev['ma_long']:
            if position['shares'] > 0:
                return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def trend_following(df: pd.DataFrame, date: str, position: Dict, capital: float,
                       trend_window: int = 60, stop_loss: float = 0.08) -> Tuple[str, int]:
        """
        趋势跟踪策略 - 减少交易频率
        
        只在明显趋势时交易
        """
        if len(df) < trend_window:
            return "HOLD", 0
        
        current_price = df.iloc[-1]['close']
        
        # 计算趋势
        df = df.copy()
        df['ma60'] = df['close'].rolling(trend_window).mean()
        df['trend'] = (df['close'] - df['ma60']) / df['ma60']
        
        current = df.iloc[-1]
        
        # 检查止损
        if position['shares'] > 0:
            avg_cost = position.get('avg_cost', 0) / position['shares'] if position['shares'] > 0 else 0
            if avg_cost > 0:
                pnl_pct = (current_price - avg_cost) / avg_cost
                if pnl_pct < -stop_loss:
                    return "SELL", position['shares']
        
        # 强势上涨趋势买入
        if current['trend'] > 0.05 and position['shares'] == 0:
            shares = int(capital / current_price / 100) * 100
            return "BUY", shares
        
        # 趋势转弱卖出
        if current['trend'] < 0 and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def buy_and_hold_with_timing(df: pd.DataFrame, date: str, position: Dict, capital: float) -> Tuple[str, int]:
        """
        择时买入持有 - 最简单有效
        
        只在市场恐慌时买入，长期持有
        """
        if len(df) < 20:
            return "HOLD", 0
        
        current_price = df.iloc[-1]['close']
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # RSI < 30 (超卖) 且空仓 = 买入
        if current_rsi < 30 and position['shares'] == 0:
            shares = int(capital / current_price / 100) * 100
            return "BUY", shares
        
        # RSI > 70 (超买) 且持仓 = 卖出
        if current_rsi > 70 and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0


if __name__ == "__main__":
    print("=" * 70)
    print("CIO改进版策略库")
    print("=" * 70)
    print("\n改进点:")
    print("1. 加入止损机制 (默认5-8%)")
    print("2. 加入止盈机制 (默认10%)")
    print("3. 减少交易频率")
    print("4. 趋势过滤")
    print("=" * 70)
