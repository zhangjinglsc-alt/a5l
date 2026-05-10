#!/usr/bin/env python3
"""
CIO历史数据处理器 - 流式处理大型zip文件
支持800MB+日K数据，不解压全部文件到磁盘
"""
import zipfile
import pandas as pd
import numpy as np
import sqlite3
import os
import sys
from io import BytesIO
from datetime import datetime
import json

class HistoricalDataProcessor:
    """历史数据流式处理器"""
    
    def __init__(self, zip_path, output_dir='data/processed'):
        self.zip_path = zip_path
        self.output_dir = output_dir
        self.db_path = os.path.join(output_dir, 'historical_data.db')
        os.makedirs(output_dir, exist_ok=True)
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_rows': 0,
            'errors': []
        }
    
    def process_zip_streaming(self, batch_size=10000):
        """
        流式处理zip文件，逐文件读取，不占用大量内存
        """
        print("=" * 70)
        print("🚀 流式处理大型zip文件")
        print("=" * 70)
        print(f"📦 Zip文件: {self.zip_path}")
        print(f"💾 输出目录: {self.output_dir}")
        print("")
        
        if not os.path.exists(self.zip_path):
            print(f"❌ 错误: 找不到文件 {self.zip_path}")
            return False
        
        # 获取zip文件信息
        file_size_mb = os.path.getsize(self.zip_path) / (1024 * 1024)
        print(f"📊 Zip文件大小: {file_size_mb:.1f} MB")
        print("")
        
        # 创建数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                UNIQUE(stock_code, date)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_date ON stock_data(stock_code, date)')
        conn.commit()
        
        # 打开zip文件
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            # 获取所有csv文件
            csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
            self.stats['total_files'] = len(csv_files)
            
            print(f"📁 发现 {len(csv_files)} 个CSV文件")
            print("")
            
            # 逐文件处理
            for idx, csv_file in enumerate(csv_files, 1):
                try:
                    print(f"[{idx}/{len(csv_files)}] 处理: {csv_file}", end='')
                    
                    # 从zip中读取文件到内存
                    with zf.open(csv_file) as f:
                        # 读取CSV到DataFrame
                        df = pd.read_csv(f)
                        
                        # 标准化列名
                        df.columns = [c.lower().strip() for c in df.columns]
                        
                        # 检查必需的列
                        required_cols = ['code', 'date', 'open', 'high', 'low', 'close', 'volume']
                        missing_cols = [c for c in required_cols if c not in df.columns]
                        
                        if missing_cols:
                            print(f" ⚠️ 缺少列: {missing_cols}")
                            continue
                        
                        # 标准化数据
                        df = self._standardize_data(df)
                        
                        # 写入数据库
                        df.to_sql('stock_data', conn, if_exists='append', index=False)
                        
                        self.stats['processed_files'] += 1
                        self.stats['total_rows'] += len(df)
                        
                        print(f" ✅ {len(df)}行")
                        
                except Exception as e:
                    error_msg = f"处理 {csv_file} 失败: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f" ❌ {error_msg}")
        
        conn.close()
        
        # 输出统计
        print("")
        print("=" * 70)
        print("📊 处理统计")
        print("=" * 70)
        print(f"   总文件数: {self.stats['total_files']}")
        print(f"   成功处理: {self.stats['processed_files']}")
        print(f"   总数据行: {self.stats['total_rows']:,}")
        print(f"   错误数: {len(self.stats['errors'])}")
        print(f"")
        print(f"💾 数据库保存: {self.db_path}")
        print(f"   大小: {os.path.getsize(self.db_path) / (1024*1024):.1f} MB")
        
        # 保存统计
        stats_path = os.path.join(self.output_dir, 'import_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        return True
    
    def _standardize_data(self, df):
        """标准化数据格式"""
        # 选择需要的列
        cols_map = {
            'code': 'stock_code',
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'amount': 'amount'
        }
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in cols_map.items() if k in df.columns})
        
        # 确保必需的列存在
        for col in ['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume']:
            if col not in df.columns:
                df[col] = 0
        
        # 添加amount列（如果不存在）
        if 'amount' not in df.columns:
            df['amount'] = df['close'] * df['volume']
        
        # 选择最终列
        df = df[['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        
        # 删除NaN
        df = df.dropna()
        
        # 转换stock_code为字符串
        df['stock_code'] = df['stock_code'].astype(str)
        
        return df
    
    def validate_data(self):
        """验证导入的数据"""
        print("")
        print("=" * 70)
        print("🔍 数据验证")
        print("=" * 70)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计股票数量
        cursor.execute('SELECT COUNT(DISTINCT stock_code) FROM stock_data')
        stock_count = cursor.fetchone()[0]
        print(f"   股票数量: {stock_count}")
        
        # 统计日期范围
        cursor.execute('SELECT MIN(date), MAX(date) FROM stock_data')
        date_range = cursor.fetchone()
        print(f"   日期范围: {date_range[0]} ~ {date_range[1]}")
        
        # 统计总记录数
        cursor.execute('SELECT COUNT(*) FROM stock_data')
        total_records = cursor.fetchone()[0]
        print(f"   总记录数: {total_records:,}")
        
        # 样本数据
        cursor.execute('SELECT * FROM stock_data LIMIT 5')
        sample = cursor.fetchall()
        print(f"")
        print("   样本数据:")
        for row in sample:
            print(f"   {row[1]} {row[2]}: O{row[3]:.2f} H{row[4]:.2f} L{row[5]:.2f} C{row[6]:.2f} V{row[7]}")
        
        conn.close()
        
        return {
            'stock_count': stock_count,
            'date_range': date_range,
            'total_records': total_records
        }


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 CIO历史数据处理器 - 流式处理版")
    print("支持800MB+大型zip文件")
    print("=" * 70)
    print("")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
    else:
        zip_path = '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/kaipanla_history.zip'
    
    output_dir = '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/processed'
    
    # 创建处理器
    processor = HistoricalDataProcessor(zip_path, output_dir)
    
    # 处理数据
    if processor.process_zip_streaming():
        # 验证数据
        stats = processor.validate_data()
        
        print("")
        print("=" * 70)
        print("✅ 数据导入完成!")
        print("=" * 70)
        print(f"")
        print("下一步:")
        print(f"   运行历史数据训练器: python3 cio_historical_trainer.py")
        print(f"   数据库位置: {processor.db_path}")
    else:
        print("")
        print("⚠️ 数据导入失败，请检查文件路径")


if __name__ == "__main__":
    main()
