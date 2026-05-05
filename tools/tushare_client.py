#!/usr/bin/env python3
"""
Tushare数据接口模块 - A5L Layer 1数据底座

功能:
- A股实时/历史行情
- 财务数据
- 龙虎榜数据
- 资金流向
- 宏观经济数据

配置:
- 需要Tushare Pro Token (从 https://tushare.pro 注册获取)
- 免费版: 部分接口可用，积分限制
- 付费版: 全量接口，更多调用次数
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
import pandas as pd

# 尝试导入tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("⚠️ Tushare未安装，请运行: pip install tushare")


class TushareDataSource:
    """Tushare数据源封装"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化Tushare数据源
        
        Args:
            token: Tushare Pro Token，如果不提供则从环境变量读取
        """
        if not TUSHARE_AVAILABLE:
            raise ImportError("Tushare未安装")
        
        # 获取token
        self.token = token or os.environ.get('TUSHARE_TOKEN')
        
        if not self.token:
            raise ValueError("请提供Tushare Token或设置环境变量TUSHARE_TOKEN")
        
        # 初始化pro接口
        self.pro = ts.pro_api(self.token)
        
        # 测试连接
        self._test_connection()
        
        print("✅ Tushare数据源初始化成功")
    
    def _test_connection(self):
        """测试连接"""
        try:
            # 测试获取股票列表
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name', limit=1)
            if df is not None and len(df) > 0:
                print(f"   连接测试成功，数据接口正常")
            else:
                print(f"   ⚠️ 连接测试返回空数据")
        except Exception as e:
            print(f"   ⚠️ 连接测试失败: {e}")
    
    # ==================== A股行情数据 ====================
    
    def get_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日线行情
        
        Args:
            ts_code: 股票代码 (如 '000001.SZ')
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            DataFrame包含: ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
        """
        try:
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_daily_basic(self, ts_code: str, trade_date: str) -> pd.DataFrame:
        """
        获取每日指标（基本面数据）
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期 (YYYYMMDD)
        
        Returns:
            DataFrame包含: 换手率、市盈率、市净率、总市值等
        """
        try:
            df = self.pro.daily_basic(ts_code=ts_code, trade_date=trade_date)
            return df
        except Exception as e:
            print(f"❌ 获取每日指标失败: {e}")
            return pd.DataFrame()
    
    def get_stock_basic(self) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Returns:
            DataFrame包含所有A股的基础信息
        """
        try:
            df = self.pro.stock_basic(exchange='', list_status='L')
            return df
        except Exception as e:
            print(f"❌ 获取股票基础信息失败: {e}")
            return pd.DataFrame()
    
    # ==================== 财务数据 ====================
    
    def get_income(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取利润表数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            df = self.pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取利润表失败: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取资产负债表"""
        try:
            df = self.pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取资产负债表失败: {e}")
            return pd.DataFrame()
    
    def get_cash_flow(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取现金流量表"""
        try:
            df = self.pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取现金流量表失败: {e}")
            return pd.DataFrame()
    
    # ==================== 另类数据（超短策略关键） ====================
    
    def get_top_list(self, trade_date: str) -> pd.DataFrame:
        """
        获取龙虎榜数据
        
        Args:
            trade_date: 交易日期 (YYYYMMDD)
        
        Returns:
            DataFrame包含龙虎榜详细信息
        """
        try:
            df = self.pro.top_list(trade_date=trade_date)
            return df
        except Exception as e:
            print(f"❌ 获取龙虎榜失败: {e}")
            return pd.DataFrame()
    
    def get_money_flow(self, trade_date: str) -> pd.DataFrame:
        """
        获取个股资金流向
        
        Args:
            trade_date: 交易日期
        """
        try:
            df = self.pro.moneyflow(trade_date=trade_date)
            return df
        except Exception as e:
            print(f"❌ 获取资金流向失败: {e}")
            return pd.DataFrame()
    
    def get_north_money(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取北向资金流向
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            df = self.pro.moneyflow_hsgt(start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取北向资金失败: {e}")
            return pd.DataFrame()
    
    # ==================== 宏观经济数据 ====================
    
    def get_gdp(self) -> pd.DataFrame:
        """获取GDP数据"""
        try:
            df = self.pro.gdp()
            return df
        except Exception as e:
            print(f"❌ 获取GDP数据失败: {e}")
            return pd.DataFrame()
    
    def get_cpi(self) -> pd.DataFrame:
        """获取CPI数据"""
        try:
            df = self.pro.cpi()
            return df
        except Exception as e:
            print(f"❌ 获取CPI数据失败: {e}")
            return pd.DataFrame()
    
    def get_shibor(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取Shibor利率"""
        try:
            df = self.pro.shibor(start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"❌ 获取Shibor失败: {e}")
            return pd.DataFrame()


def setup_tushare():
    """设置Tushare配置"""
    config_path = '/workspace/projects/workspace/config/tushare_config.json'
    
    print("=" * 60)
    print("🔧 Tushare配置向导")
    print("=" * 60)
    print()
    print("请访问 https://tushare.pro 注册并获取Token")
    print()
    
    token = input("请输入Tushare Pro Token: ").strip()
    
    if not token:
        print("❌ Token不能为空")
        return None
    
    config = {
        'token': token,
        'setup_date': datetime.now().isoformat(),
        'status': 'active'
    }
    
    # 保存配置
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # 设置环境变量
    os.environ['TUSHARE_TOKEN'] = token
    
    print()
    print("✅ Tushare配置已保存")
    print(f"   配置文件: {config_path}")
    
    # 测试连接
    try:
        ds = TushareDataSource(token=token)
        print()
        print("🎉 Tushare配置成功！")
        return ds
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return None


def test_basic_functions():
    """测试基本功能"""
    print()
    print("=" * 60)
    print("🧪 Tushare功能测试")
    print("=" * 60)
    
    # 读取配置
    config_path = '/workspace/projects/workspace/config/tushare_config.json'
    if not os.path.exists(config_path):
        print("⚠️ 未找到配置文件，请先运行 setup_tushare()")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    token = config.get('token')
    
    try:
        ds = TushareDataSource(token=token)
        
        # 测试1: 获取股票列表
        print()
        print("测试1: 获取A股股票列表...")
        stocks = ds.get_stock_basic()
        if len(stocks) > 0:
            print(f"   ✅ 成功获取 {len(stocks)} 只股票信息")
            print(f"   示例: {stocks.iloc[0]['ts_code']} - {stocks.iloc[0]['name']}")
        
        # 测试2: 获取日线数据
        print()
        print("测试2: 获取日线行情 (000001.SZ)...")
        today = datetime.now()
        start = (today - timedelta(days=10)).strftime('%Y%m%d')
        end = today.strftime('%Y%m%d')
        df = ds.get_daily('000001.SZ', start, end)
        if len(df) > 0:
            print(f"   ✅ 成功获取 {len(df)} 条日线数据")
            print(f"   最新: 收盘价 {df.iloc[0]['close']}")
        
        # 测试3: 获取龙虎榜 (需要积分)
        print()
        print("测试3: 获取龙虎榜数据...")
        yesterday = (today - timedelta(days=1)).strftime('%Y%m%d')
        top = ds.get_top_list(yesterday)
        if len(top) > 0:
            print(f"   ✅ 成功获取 {len(top)} 条龙虎榜数据")
        else:
            print("   ⚠️ 暂无龙虎榜数据（可能需要积分）")
        
        print()
        print("=" * 60)
        print("✅ Tushare功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup':
            setup_tushare()
        elif sys.argv[1] == 'test':
            test_basic_functions()
        else:
            print("用法: python3 tushare_client.py [setup|test]")
    else:
        print("Tushare数据接口模块已加载")
        print()
        print("使用方法:")
        print("  1. 配置: python3 tushare_client.py setup")
        print("  2. 测试: python3 tushare_client.py test")
        print()
        print("或直接导入:")
        print("  from tools.tushare_client import TushareDataSource")
        print("  ds = TushareDataSource()")
