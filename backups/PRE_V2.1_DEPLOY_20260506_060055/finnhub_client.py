#!/usr/bin/env python3
"""
Finnhub数据接口 - A5L美股数据模块
来自OpenStock项目，用于美股实时数据获取

API限流控制:
- 免费版: 60次/分钟
- 建议频率: 每15分钟更新一次 (32次/小时, 0.5次/分钟)
- 安全余量: 95%
"""

import os
import json
import time
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


class RateLimiter:
    """API限流控制器 - 确保不超过Finnhub限制"""
    
    def __init__(self, max_requests_per_minute: int = 60, safety_margin: float = 0.8):
        """
        初始化限流器
        
        Args:
            max_requests_per_minute: 每分钟最大请求数 (免费版=60)
            safety_margin: 安全余量 (默认80%，即最多48次/分钟)
        """
        self.max_requests = int(max_requests_per_minute * safety_margin)  # 48次/分钟
        self.requests = []  # 记录请求时间戳
        self.min_delay = 60.0 / self.max_requests  # 最小间隔1.25秒
        self.last_request_time = 0
        
    def wait_if_needed(self):
        """检查是否需要等待以避免超限"""
        now = time.time()
        
        # 清理1分钟前的请求记录
        self.requests = [t for t in self.requests if now - t < 60]
        
        # 检查是否需要等待
        if len(self.requests) >= self.max_requests:
            # 需要等待
            oldest_request = self.requests[0]
            wait_time = 60 - (now - oldest_request) + 0.1  # 多等0.1秒确保
            if wait_time > 0:
                print(f"   ⏸️ 接近API限制，等待{wait_time:.1f}秒...")
                time.sleep(wait_time)
                self.requests = []  # 清空记录
        
        # 确保最小间隔
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)
        
        # 记录本次请求
        self.requests.append(time.time())
        self.last_request_time = time.time()
        
    def get_stats(self) -> Dict:
        """获取当前限流统计"""
        now = time.time()
        self.requests = [t for t in self.requests if now - t < 60]
        return {
            'requests_in_last_minute': len(self.requests),
            'max_allowed': self.max_requests,
            'usage_pct': len(self.requests) / self.max_requests * 100,
            'min_delay': self.min_delay
        }


class FinnhubDataSource:
    """Finnhub数据源封装 - 美股实时数据 (带限流控制)"""
    
    def __init__(self, api_key: Optional[str] = None, enable_rate_limit: bool = True):
        """
        初始化Finnhub数据源
        
        Args:
            api_key: Finnhub API Key，如果不提供则从配置文件读取
            enable_rate_limit: 是否启用限流控制 (默认True)
        """
        if not FINNHUB_AVAILABLE:
            raise ImportError("Finnhub未安装")
        
        # 获取API Key
        self.api_key = api_key or self._load_api_key()
        
        if not self.api_key:
            raise ValueError("请提供Finnhub API Key或设置配置文件")
        
        # 初始化限流器 (60次/分钟 * 80%安全余量 = 48次/分钟)
        self.rate_limiter = RateLimiter(max_requests_per_minute=60, safety_margin=0.8) if enable_rate_limit else None
        
        # 初始化客户端
        self.client = finnhub.Client(api_key=self.api_key)
        
        # 测试连接
        self._test_connection()
        
        print("✅ Finnhub数据源初始化成功 (限流控制已启用)")
        if self.rate_limiter:
            stats = self.rate_limiter.get_stats()
            print(f"   限流配置: 最多{stats['max_allowed']}次/分钟, 最小间隔{stats['min_delay']:.2f}秒")
    
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
        获取股票实时报价 (带限流控制)
        
        Args:
            symbol: 股票代码 (如 'AAPL', 'NVDA')
        
        Returns:
            实时报价数据
        """
        # 限流检查
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
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
        获取公司基本信息 (带限流控制)
        
        Args:
            symbol: 股票代码
        
        Returns:
            公司资料
        """
        # 限流检查
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
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
        获取财务报表 (带限流控制)
        
        Args:
            symbol: 股票代码
        
        Returns:
            财务数据
        """
        # 限流检查
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
        try:
            financials = self.client.financials(symbol, 'annual', 'bs')
            return financials
        except Exception as e:
            print(f"❌ 获取{symbol}财务数据失败: {e}")
            return {}
    
    def get_news(self, symbol: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        获取公司新闻 (带限流控制)
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            新闻列表
        """
        # 限流检查
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
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
        获取市场新闻 (带限流控制)
        
        Args:
            category: 新闻类别 (general/forex/crypto/merger)
        
        Returns:
            新闻列表
        """
        # 限流检查
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
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
    
    def get_multiple_quotes(self, symbols: List[str], show_progress: bool = True) -> Dict[str, Dict]:
        """
        批量获取多个股票报价 (带限流控制和进度显示)
        
        Args:
            symbols: 股票代码列表
            show_progress: 是否显示进度
        
        Returns:
            报价字典
        """
        results = {}
        total = len(symbols)
        
        for i, symbol in enumerate(symbols, 1):
            if show_progress and self.rate_limiter:
                stats = self.rate_limiter.get_stats()
                print(f"   [{i}/{total}] 获取{symbol}... (API使用: {stats['usage_pct']:.1f}%)")
            
            results[symbol] = self.get_quote(symbol)
        
        return results
    
    def get_rate_limit_stats(self) -> Dict:
        """
        获取当前API限流统计
        
        Returns:
            限流统计信息
        """
        if self.rate_limiter:
            return self.rate_limiter.get_stats()
        return {'rate_limiting': 'disabled'}
    
    def print_rate_limit_status(self):
        """打印当前限流状态"""
        stats = self.get_rate_limit_stats()
        print("="*60)
        print("📊 Finnhub API限流状态")
        print("="*60)
        if stats.get('rate_limiting') == 'disabled':
            print("   限流控制: 已禁用")
        else:
            print(f"   最近1分钟请求: {stats['requests_in_last_minute']}次")
            print(f"   最大允许: {stats['max_allowed']}次/分钟")
            print(f"   使用率: {stats['usage_pct']:.1f}%")
            print(f"   最小间隔: {stats['min_delay']:.2f}秒")
            if stats['usage_pct'] > 80:
                print("   ⚠️ 警告: 接近API限制!")
            else:
                print("   ✅ 状态: 正常")
        print("="*60)


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
