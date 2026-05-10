#!/usr/bin/env python3
"""
A5L Strategy Library v1.0
交易策略库 - 支持多种经典和自定义策略
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class StrategyLibrary:
    """策略库 - 包含多种交易策略"""
    
    # ==================== 趋势跟踪策略 ====================
    
    @staticmethod
    def ma_cross_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float, 
                         short_window: int = 5, long_window: int = 20) -> Tuple[str, int]:
        """
        双均线交叉策略
        
        Args:
            short_window: 短期均线窗口
            long_window: 长期均线窗口
        """
        if len(df) < long_window:
            return "HOLD", 0
        
        df = df.copy()
        df['ma_short'] = df['close'].rolling(short_window).mean()
        df['ma_long'] = df['close'].rolling(long_window).mean()
        
        current = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else current
        
        # 金叉买入
        if current['ma_short'] > current['ma_long'] and prev['ma_short'] <= prev['ma_long']:
            if position['shares'] == 0:
                shares = int(capital / current['close'] / 100) * 100
                return "BUY", shares
        
        # 死叉卖出
        elif current['ma_short'] < current['ma_long'] and prev['ma_short'] >= prev['ma_long']:
            if position['shares'] > 0:
                return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def turtle_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                       entry_window: int = 20, exit_window: int = 10) -> Tuple[str, int]:
        """
        海龟交易策略 - 唐奇安通道突破
        
        Args:
            entry_window: 入场窗口 (默认20日新高)
            exit_window: 出场窗口 (默认10日新低)
        """
        if len(df) < entry_window:
            return "HOLD", 0
        
        current = df.iloc[-1]
        
        # 计算唐奇安通道
        high_20 = df['high'].rolling(entry_window).max().iloc[-1]
        low_10 = df['low'].rolling(exit_window).min().iloc[-1]
        
        # 突破上轨买入
        if current['close'] >= high_20 and position['shares'] == 0:
            shares = int(capital / current['close'] / 100) * 100
            return "BUY", shares
        
        # 跌破下轨卖出
        elif current['close'] <= low_10 and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    # ==================== 动量策略 ====================
    
    @staticmethod
    def momentum_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                         momentum_window: int = 5, threshold: float = 0.05) -> Tuple[str, int]:
        """
        动量策略 - N日涨幅突破阈值
        
        Args:
            momentum_window: 动量计算窗口
            threshold: 动量阈值
        """
        if len(df) < momentum_window:
            return "HOLD", 0
        
        current_price = df.iloc[-1]['close']
        past_price = df.iloc[-momentum_window]['close']
        momentum = (current_price - past_price) / past_price
        
        # 动量突破买入
        if momentum > threshold and position['shares'] == 0:
            shares = int(capital / current_price / 100) * 100
            return "BUY", shares
        
        # 动量转负卖出
        elif momentum < 0 and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def rsi_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                    rsi_window: int = 14, oversold: float = 30, overbought: float = 70) -> Tuple[str, int]:
        """
        RSI策略 - 相对强弱指标
        
        Args:
            rsi_window: RSI计算窗口
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        if len(df) < rsi_window + 1:
            return "HOLD", 0
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        current_price = df.iloc[-1]['close']
        
        # 超卖买入
        if current_rsi < oversold and position['shares'] == 0:
            shares = int(capital / current_price / 100) * 100
            return "BUY", shares
        
        # 超买卖出
        elif current_rsi > overbought and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def macd_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                     fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[str, int]:
        """
        MACD策略 - 指数平滑异同移动平均线
        
        Args:
            fast: 快线窗口
            slow: 慢线窗口
            signal: 信号线窗口
        """
        if len(df) < slow + signal:
            return "HOLD", 0
        
        # 计算MACD
        exp1 = df['close'].ewm(span=fast).mean()
        exp2 = df['close'].ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        current_price = df.iloc[-1]['close']
        
        # MACD金叉买入
        if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
            if position['shares'] == 0:
                shares = int(capital / current_price / 100) * 100
                return "BUY", shares
        
        # MACD死叉卖出
        elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
            if position['shares'] > 0:
                return "SELL", position['shares']
        
        return "HOLD", 0
    
    # ==================== 价值投资策略 ====================
    
    @staticmethod
    def pe_valuation_strategy(pe_ratio: float, pb_ratio: float, position: Dict, 
                              capital: float, price: float,
                              pe_threshold: float = 15, pb_threshold: float = 1.5) -> Tuple[str, int]:
        """
        估值策略 - 低PE/PB买入
        
        Args:
            pe_ratio: 市盈率
            pb_ratio: 市净率
            pe_threshold: PE阈值
            pb_threshold: PB阈值
        """
        # 低估值买入
        if pe_ratio < pe_threshold and pb_ratio < pb_threshold and position['shares'] == 0:
            shares = int(capital / price / 100) * 100
            return "BUY", shares
        
        # 高估值卖出
        elif (pe_ratio > pe_threshold * 2 or pb_ratio > pb_threshold * 2) and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    # ==================== 量价策略 ====================
    
    @staticmethod
    def volume_price_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                             vol_window: int = 20) -> Tuple[str, int]:
        """
        量价策略 - 放量突破
        
        Args:
            vol_window: 成交量均线窗口
        """
        if len(df) < vol_window:
            return "HOLD", 0
        
        df = df.copy()
        df['vol_ma'] = df['vol'].rolling(vol_window).mean()
        
        current = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else current
        
        # 放量上涨买入
        if (current['close'] > prev['close'] and 
            current['vol'] > current['vol_ma'] * 1.5 and
            position['shares'] == 0):
            shares = int(capital / current['close'] / 100) * 100
            return "BUY", shares
        
        # 缩量下跌卖出
        elif (current['close'] < prev['close'] and 
              current['vol'] < current['vol_ma'] * 0.7 and
              position['shares'] > 0):
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    @staticmethod
    def limit_up_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float,
                          limit_up_pct: float = 0.099) -> Tuple[str, int]:
        """
        涨停策略 - 涨停板追入/打板
        
        Args:
            limit_up_pct: 涨停幅度 (默认9.9%)
        """
        if len(df) < 2:
            return "HOLD", 0
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 计算涨跌幅
        pct_change = (current['close'] - prev['close']) / prev['close']
        
        # 涨停买入 (追板策略)
        if pct_change >= limit_up_pct and position['shares'] == 0:
            # 检查是否有开板后回封
            if current['low'] < current['close']:  # 有开板
                shares = int(capital / current['close'] / 100) * 100
                return "BUY", shares
        
        # 次日高开卖出 (一日游)
        if position['shares'] > 0:
            buy_price = position.get('cost', 0) / position['shares']
            current_pnl = (current['close'] - buy_price) / buy_price
            
            # 盈利超过3%或亏损超过2%都卖出
            if current_pnl > 0.03 or current_pnl < -0.02:
                return "SELL", position['shares']
        
        return "HOLD", 0
    
    # ==================== 组合策略 ====================
    
    @staticmethod
    def multi_factor_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float) -> Tuple[str, int]:
        """
        多因子组合策略
        结合趋势、动量、RSI三个指标
        """
        if len(df) < 20:
            return "HOLD", 0
        
        # 计算各指标
        df = df.copy()
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        # 动量
        momentum = (df.iloc[-1]['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current = df.iloc[-1]
        current_price = current['close']
        
        # 综合评分
        score = 0
        if current['ma5'] > current['ma20']: score += 1  # 趋势向上
        if momentum > 0.03: score += 1  # 动量强劲
        if 30 < rsi.iloc[-1] < 70: score += 1  # RSI健康
        
        # 评分>=2买入
        if score >= 2 and position['shares'] == 0:
            shares = int(capital / current_price / 100) * 100
            return "BUY", shares
        
        # 评分<1卖出
        elif score < 1 and position['shares'] > 0:
            return "SELL", position['shares']
        
        return "HOLD", 0
    
    # ==================== 策略选择器 ====================
    
    @classmethod
    def get_strategy(cls, name: str):
        """获取策略函数"""
        strategies = {
            'ma_cross': cls.ma_cross_strategy,
            'turtle': cls.turtle_strategy,
            'momentum': cls.momentum_strategy,
            'rsi': cls.rsi_strategy,
            'macd': cls.macd_strategy,
            'volume_price': cls.volume_price_strategy,
            'limit_up': cls.limit_up_strategy,
            'multi_factor': cls.multi_factor_strategy,
        }
        return strategies.get(name, cls.ma_cross_strategy)
    
    @classmethod
    def list_strategies(cls) -> Dict:
        """列出所有可用策略"""
        return {
            'ma_cross': {
                'name': '双均线交叉',
                'category': '趋势跟踪',
                'description': '短期均线上穿长期均线买入，下穿卖出',
                'params': {'short_window': 5, 'long_window': 20}
            },
            'turtle': {
                'name': '海龟交易',
                'category': '趋势跟踪',
                'description': '突破N日新高买入，跌破N日新低卖出',
                'params': {'entry_window': 20, 'exit_window': 10}
            },
            'momentum': {
                'name': '动量策略',
                'category': '动量策略',
                'description': 'N日涨幅突破阈值买入',
                'params': {'momentum_window': 5, 'threshold': 0.05}
            },
            'rsi': {
                'name': 'RSI策略',
                'category': '动量策略',
                'description': 'RSI超卖买入，超买卖出',
                'params': {'rsi_window': 14, 'oversold': 30, 'overbought': 70}
            },
            'macd': {
                'name': 'MACD策略',
                'category': '动量策略',
                'description': 'MACD金叉买入，死叉卖出',
                'params': {'fast': 12, 'slow': 26, 'signal': 9}
            },
            'volume_price': {
                'name': '量价策略',
                'category': '量价策略',
                'description': '放量上涨买入，缩量下跌卖出',
                'params': {'vol_window': 20}
            },
            'limit_up': {
                'name': '涨停策略',
                'category': '事件驱动',
                'description': '涨停板追入，次日止盈止损',
                'params': {'limit_up_pct': 0.099}
            },
            'multi_factor': {
                'name': '多因子组合',
                'category': '组合策略',
                'description': '趋势+动量+RSI综合评分',
                'params': {}
            }
        }


if __name__ == "__main__":
    # 列出所有策略
    print("=" * 70)
    print("A5L Strategy Library v1.0")
    print("=" * 70)
    
    strategies = StrategyLibrary.list_strategies()
    
    for code, info in strategies.items():
        print(f"\n📊 {info['name']} ({code})")
        print(f"   类别: {info['category']}")
        print(f"   描述: {info['description']}")
        print(f"   参数: {info['params']}")
    
    print("\n" + "=" * 70)
