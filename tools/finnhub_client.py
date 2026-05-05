#!/usr/bin/env python3
"""
Finnhub数据接口 - A5L美股数据模块
来自OpenStock项目，用于美股实时数据获取
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd

# 尝试导入finnhub
try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    print("⚠️ Finnhub未安装，请运行: pip install finnhub-python")


class FinnhubDataSource:
    """Finnhub数据源封装 - 美股实时数据"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Finnhub数据源
        
        Args:
            api_key: Finnhub API Key，如果不提供则从配置文件读取
        """
        if not FINNHUB_AVAILABLE:
            raise ImportError("Finnhub未安装")
        
        # 获取API Key
        self.api_key = api_key or self._load_api_key()
        
        if not self.api_key:
            raise ValueError("请提供Finnhub API Key或设置配置文件")
        
        # 初始化客户端
        self.client = finnhub.Client(api_key=self.api_key)
        
        # 测试连接
        self._test_connection()
        
        print("✅ Finnhub数据源初始化成功")
    
    def _load_api_key(self) -> Optional[str]:
        """从配置文件加载API Key"""
        config_path = '/workspace/projects/workspace/config/finnhub_config.json'
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('api_key')
        
        # 尝试环境变量
        return os.environ.get('FINNHUB_API_KEY')
    
    def _test_connection(self):
        """测试连接"""
        try:
            # 测试获取AAPL报价
            quote = self.client.quote('AAPL')
            if quote:
                print(f"   连接测试成功，AAPL当前价: ${quote.get('c', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ 连接测试: {e}")
    
    # ==================== 美股行情数据 ====================
    
    def get_quote(self, symbol: str) -> Dict:
        """
        获取股票实时报价
        
        Args:
            symbol: 股票代码 (如 'AAPL', 'NVDA')
        
        Returns:
            实时报价数据
        """
        try:
            quote = self.client.quote(symbol)
            return {
                'symbol': symbol,
                'current': quote.get('c'),  # 当前价
                'change': quote.get('d'),  # 涨跌额
                'change_pct': quote.get('dp'),  # 涨跌幅%
                'high': quote.get('h'),  # 当日最高
                'low': quote.get('l'),  # 当日最低
                'open': quote.get('o'),  # 开盘价
                'previous_close': quote.get('pc'),  # 昨收
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ 获取{symbol}报价失败: {e}")
            return {}
    
    def get_company_profile(self, symbol: str) -> Dict:
        """
        获取公司基本信息
        
        Args:
            symbol: 股票代码
        
        Returns:
            公司资料
        """
        try:
            profile = self.client.company_profile2(symbol=symbol)
            return {
                'symbol': symbol,
                'name': profile.get('name'),
                'industry': profile.get('industry'),
                'sector': profile.get('sector'),
                'market_cap': profile.get('marketCapitalization'),  # 市值(百万)
                'website': profile.get('weburl'),
                'country': profile.get('country'),
                'currency': profile.get('currency')
            }
        except Exception as e:
            print(f"❌ 获取{symbol}公司资料失败: {e}")
            return {}
    
    def get_financials(self, symbol: str) -> Dict:
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
        
        Returns:
            财务数据
        """
        try:
            financials = self.client.financials(symbol, 'annual', 'bs')
            return financials
        except Exception as e:
            print(f"❌ 获取{symbol}财务数据失败: {e}")
            return {}
    
    def get_news(self, symbol: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        获取公司新闻
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            新闻列表
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            news = self.client.company_news(symbol, start_date, end_date)
            return news
        except Exception as e:
            print(f"❌ 获取{symbol}新闻失败: {e}")
            return []
    
    def get_market_news(self, category: str = 'general') -> List[Dict]:
        """
        获取市场新闻
        
        Args:
            category: 新闻类别 (general/forex/crypto/merger)
        
        Returns:
            新闻列表
        """
        try:
            news = self.client.general_news(category)
            return news
        except Exception as e:
            print(f"❌ 获取市场新闻失败: {e}")
            return []
    
    # ==================== 实时数据流 ====================
    
    def get_market_status(self, exchange: str = 'US') -> Dict:
        """
        获取市场状态
        
        Args:
            exchange: 交易所 (US)
        
        Returns:
            市场状态信息
        """
        try:
            status = self.client.market_status(exchange=exchange)
            return status
        except Exception as e:
            print(f"❌ 获取市场状态失败: {e}")
            return {}
    
    # ==================== 快捷方法 ====================
    
    def get_us_stock_quote(self, symbol: str) -> Dict:
        """快捷获取美股报价"""
        return self.get_quote(symbol)
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        批量获取多个股票报价
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            报价字典
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_quote(symbol)
        return results


def setup_finnhub():
    """设置Finnhub配置"""
    print("=" * 60)
    print("🔧 Finnhub配置向导")
    print("=" * 60)
    print()
    print("请访问 https://finnhub.io 获取免费API Key")
    print()
    
    api_key = input("请输入Finnhub API Key: ").strip()
    
    if not api_key:
        print("❌ API Key不能为空")
        return None
    
    config = {
        'api_key': api_key,
        'setup_date': datetime.now().isoformat(),
        'status': 'active'
    }
    
    # 保存配置
    config_path = '/workspace/projects/workspace/config/finnhub_config.json'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # 设置环境变量
    os.environ['FINNHUB_API_KEY'] = api_key
    
    print()
    print("✅ Finnhub配置已保存")
    print(f"   配置文件: {config_path}")
    
    # 测试连接
    try:
        ds = FinnhubDataSource(api_key=api_key)
        print()
        print("🎉 Finnhub配置成功！")
        return ds
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return None


# 快捷函数
def get_finnhub_client() -> FinnhubDataSource:
    """获取Finnhub客户端实例"""
    return FinnhubDataSource()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_finnhub()
    else:
        print("=" * 60)
        print("🚀 Finnhub数据源测试")
        print("=" * 60)
        
        try:
            ds = FinnhubDataSource()
            
            # 测试1: 获取NVDA报价
            print("\n📊 测试1: NVDA实时报价")
            quote = ds.get_quote('NVDA')
            if quote:
                print(f"   当前价: ${quote['current']}")
                print(f"   涨跌幅: {quote['change_pct']:.2f}%")
            
            # 测试2: 获取公司资料
            print("\n📊 测试2: NVDA公司资料")
            profile = ds.get_company_profile('NVDA')
            if profile:
                print(f"   公司名称: {profile['name']}")
                print(f"   行业: {profile['industry']}")
                print(f"   市值: ${profile['market_cap']:.2f}B")
            
            # 测试3: 获取市场新闻
            print("\n📊 测试3: 市场新闻")
            news = ds.get_market_news()
            if news:
                print(f"   获取到 {len(news)} 条新闻")
                print(f"   最新: {news[0]['headline'][:50]}...")
            
            print("\n✅ 测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
