#!/usr/bin/env python3
"""
FinceptTerminal - 金融数据终端解析器
A5L CIO觉醒系统专用数据解析模块
"""
import pandas as pd
import numpy as np
import zipfile
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
import sys

class FinceptTerminal:
    """
    金融数据解析终端
    支持多种数据格式的解析和标准化
    """
    
    def __init__(self, output_dir='data/processed'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_rows': 0,
            'errors': []
        }
    
    def parse_zip_file(self, zip_path, file_pattern='*.csv'):
        """
        解析zip文件中的数据
        支持大文件流式处理
        """
        print(f"📦 解析ZIP文件: {zip_path}")
        print(f"   文件大小: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")
        print()
        
        all_data = []
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 列出所有文件
            all_files = zf.namelist()
            csv_files = [f for f in all_files if f.endswith('.csv') or f.endswith('.txt')]
            
            print(f"   发现 {len(csv_files)} 个数据文件")
            print()
            
            for idx, filename in enumerate(csv_files, 1):
                try:
                    print(f"[{idx}/{len(csv_files)}] 解析: {filename}", end='')
                    
                    with zf.open(filename) as f:
                        # 尝试不同编码
                        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
                        df = None
                        
                        for encoding in encodings:
                            try:
                                f.seek(0)
                                df = pd.read_csv(f, encoding=encoding)
                                break
                            except:
                                continue
                        
                        if df is None:
                            print(f" ❌ 无法解码")
                            continue
                        
                        # 标准化列名
                        df = self._standardize_columns(df)
                        
                        # 提取股票代码（从文件名）
                        stock_code = self._extract_stock_code(filename)
                        if stock_code:
                            df['stock_code'] = stock_code
                        
                        all_data.append(df)
                        self.stats['processed_files'] += 1
                        self.stats['total_rows'] += len(df)
                        
                        print(f" ✅ {len(df)}行")
                        
                except Exception as e:
                    error_msg = f"解析 {filename} 失败: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f" ❌ {error_msg}")
        
        # 合并所有数据
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            print(f"\n✅ 合并完成: {len(combined)} 行数据")
            return combined
        else:
            print("\n❌ 没有成功解析的数据")
            return None
    
    def _standardize_columns(self, df):
        """标准化列名"""
        # 列名映射表（支持多种常见命名）
        column_mapping = {
            # 股票代码
            'code': 'stock_code',
            '股票代码': 'stock_code',
            'stock': 'stock_code',
            'symbol': 'stock_code',
            'ts_code': 'stock_code',
            
            # 日期
            'date': 'trade_date',
            '日期': 'trade_date',
            'trade_date': 'trade_date',
            'datetime': 'trade_date',
            'time': 'trade_date',
            
            # 开盘价
            'open': 'open',
            '开盘价': 'open',
            'open_price': 'open',
            
            # 最高价
            'high': 'high',
            '最高价': 'high',
            'high_price': 'high',
            
            # 最低价
            'low': 'low',
            '最低价': 'low',
            'low_price': 'low',
            
            # 收盘价
            'close': 'close',
            '收盘价': 'close',
            'close_price': 'close',
            
            # 成交量
            'volume': 'volume',
            '成交量': 'volume',
            'vol': 'volume',
            'volume_count': 'volume',
            
            # 成交额
            'amount': 'amount',
            '成交额': 'amount',
            'turnover': 'amount',
            'money': 'amount'
        }
        
        # 转换为小写并去除空格
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        # 应用映射
        df = df.rename(columns=column_mapping)
        
        return df
    
    def _extract_stock_code(self, filename):
        """从文件名提取股票代码"""
        import re
        # 匹配6位数字（A股代码）
        match = re.search(r'(\d{6})', filename)
        if match:
            return match.group(1)
        return None
    
    def validate_data(self, df):
        """验证数据质量"""
        print("\n🔍 数据质量验证...")
        
        required_cols = ['stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume']
        
        # 检查必需列
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            print(f"   ⚠️ 缺少列: {missing_cols}")
            return False
        
        # 检查数据类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 检查异常值
        null_count = df[required_cols].isnull().sum().sum()
        if null_count > 0:
            print(f"   ⚠️ 发现 {null_count} 个空值")
            df = df.dropna(subset=required_cols)
        
        # 检查价格逻辑 (high >= low, high >= close >= low 等)
        invalid_prices = df[
            (df['high'] < df['low']) | 
            (df['high'] < df['close']) | 
            (df['low'] > df['close']) |
            (df['open'] > df['high']) |
            (df['open'] < df['low'])
        ]
        
        if len(invalid_prices) > 0:
            print(f"   ⚠️ 发现 {len(invalid_prices)} 条价格异常数据")
            df = df[~df.index.isin(invalid_prices.index)]
        
        print(f"   ✅ 验证通过: {len(df)} 行有效数据")
        return df
    
    def export_to_sqlite(self, df, db_name='historical_data.db'):
        """导出到SQLite数据库"""
        db_path = os.path.join(self.output_dir, db_name)
        
        print(f"\n💾 导出到SQLite: {db_path}")
        
        conn = sqlite3.connect(db_path)
        
        # 创建表
        df.to_sql('stock_daily', conn, if_exists='replace', index=False)
        
        # 创建索引
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_date ON stock_daily(stock_code, trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON stock_daily(trade_date)')
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ 导出完成: {len(df)} 行")
        print(f"   📊 数据库大小: {os.path.getsize(db_path) / (1024*1024):.1f} MB")
        
        return db_path
    
    def generate_report(self):
        """生成处理报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'summary': {
                'total_files': self.stats['total_files'],
                'processed_files': self.stats['processed_files'],
                'total_rows': self.stats['total_rows'],
                'error_count': len(self.stats['errors'])
            }
        }
        
        report_path = os.path.join(self.output_dir, 'fincept_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 报告已保存: {report_path}")
        return report
    
    def process(self, zip_path):
        """完整处理流程"""
        print("=" * 70)
        print("🚀 FinceptTerminal - 金融数据解析终端")
        print("=" * 70)
        print()
        
        # 1. 解析ZIP
        df = self.parse_zip_file(zip_path)
        if df is None:
            return None
        
        # 2. 验证数据
        df = self.validate_data(df)
        if df is None or len(df) == 0:
            return None
        
        # 3. 导出到SQLite
        db_path = self.export_to_sqlite(df)
        
        # 4. 生成报告
        self.generate_report()
        
        print("\n" + "=" * 70)
        print("✅ 数据处理完成!")
        print("=" * 70)
        print(f"\n📊 统计:")
        print(f"   股票数量: {df['stock_code'].nunique()}")
        print(f"   日期范围: {df['trade_date'].min()} ~ {df['trade_date'].max()}")
        print(f"   总记录数: {len(df):,}")
        print(f"\n💾 输出:")
        print(f"   数据库: {db_path}")
        
        return db_path


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FinceptTerminal - 金融数据解析器')
    parser.add_argument('zip_file', help='ZIP文件路径')
    parser.add_argument('-o', '--output', default='data/processed', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建解析器并处理
    terminal = FinceptTerminal(output_dir=args.output)
    result = terminal.process(args.zip_file)
    
    if result:
        print(f"\n🎉 成功! 数据库: {result}")
        return 0
    else:
        print("\n❌ 处理失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
