#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L 真实数据连接器示例
修复Layer 1的关键缺口：接入AKShare真实数据

这个文件演示如何将Layer 1从框架变为真实可用的数据层
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AKShareRealConnector:
    """AKShare真实数据连接器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/market/real"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 检查akshare是否安装
        try:
            import akshare as ak
            self.ak = ak
            self.available = True
            logger.info("✅ AKShare模块已加载")
        except ImportError:
            self.available = False
            logger.warning("⚠️ AKShare未安装，运行: pip install akshare")
    
    def fetch_stock_daily(self, symbol: str, start_date: str = None, 
                         end_date: str = None) -> Optional[Dict]:
        """
        获取股票日线数据（真实AKShare调用）
        
        Args:
            symbol: 股票代码，如 "000001" (平安银行)
            start_date: 开始日期 "YYYYMMDD"
            end_date: 结束日期 "YYYYMMDD"
        
        Returns:
            包含OHLCV数据的字典
        """
        if not self.available:
            logger.error("❌ AKShare不可用，无法获取真实数据")
            return None
        
        try:
            logger.info(f"🔍 正在获取 {symbol} 的历史数据...")
            
            # 调用AKShare获取A股历史数据
            df = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                logger.warning(f"⚠️ {symbol} 返回空数据")
                return None
            
            # 转换为字典格式
            data = {
                "symbol": symbol,
                "source": "akshare",
                "fetch_time": datetime.now().isoformat(),
                "record_count": len(df),
                "data": df.to_dict('records')
            }
            
            # 保存到本地
            self._save_to_cache(symbol, data)
            
            logger.info(f"✅ 成功获取 {symbol}: {len(df)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"❌ 获取 {symbol} 数据失败: {str(e)}")
            return None
    
    def fetch_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取实时行情（需要交易日）
        
        注意：AKShare的实时接口需要交易日才能返回数据
        """
        if not self.available:
            return None
        
        try:
            # 获取实时行情
            df = self.ak.stock_bid_ask_em(symbol=symbol)
            
            return {
                "symbol": symbol,
                "source": "akshare_realtime",
                "fetch_time": datetime.now().isoformat(),
                "bid_ask": df.to_dict('records')
            }
        except Exception as e:
            logger.error(f"❌ 获取实时行情失败: {str(e)}")
            return None
    
    def fetch_stock_list(self) -> List[Dict]:
        """获取A股股票列表"""
        if not self.available:
            return []
        
        try:
            df = self.ak.stock_zh_a_spot_em()
            
            # 只取关键字段
            stocks = []
            for _, row in df.head(100).iterrows():  # 先取前100只
                stocks.append({
                    "symbol": row.get("代码"),
                    "name": row.get("名称"),
                    "price": row.get("最新价"),
                    "change_pct": row.get("涨跌幅")
                })
            
            logger.info(f"✅ 获取股票列表: {len(stocks)} 只")
            return stocks
            
        except Exception as e:
            logger.error(f"❌ 获取股票列表失败: {str(e)}")
            return []
    
    def _save_to_cache(self, symbol: str, data: Dict):
        """保存到本地缓存"""
        filename = f"{symbol}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 数据已缓存: {filepath}")

def demo():
    """演示真实数据获取"""
    print("=" * 70)
    print("🔌 AKShare真实数据连接器演示")
    print("=" * 70)
    
    connector = AKShareRealConnector()
    
    if not connector.available:
        print("\n⚠️ AKShare未安装，请先安装:")
        print("   pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple")
        return
    
    # 1. 获取股票列表
    print("\n📊 获取A股股票列表（前10只）...")
    stocks = connector.fetch_stock_list()
    for stock in stocks[:10]:
        print(f"  {stock['symbol']} - {stock['name']} - ¥{stock['price']}")
    
    # 2. 获取单只股票历史数据
    print("\n📈 获取平安银行(000001)近30天数据...")
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    data = connector.fetch_stock_daily(
        symbol="000001",
        start_date=start_date,
        end_date=end_date
    )
    
    if data:
        print(f"✅ 成功获取 {data['record_count']} 条记录")
        if data['record_count'] > 0:
            latest = data['data'][-1]
            print(f"   最新日期: {latest.get('日期')}")
            print(f"   收盘价: ¥{latest.get('收盘')}")
            print(f"   成交量: {latest.get('成交量', 0)/10000:.0f}万手")
    
    print("\n" + "=" * 70)
    print("✅ 演示完成！Layer 1现在可以获取真实数据了！")
    print("=" * 70)

if __name__ == "__main__":
    demo()
