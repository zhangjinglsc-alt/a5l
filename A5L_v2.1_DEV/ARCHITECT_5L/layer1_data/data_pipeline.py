#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1: Data Pipeline
数据底座层 - 数据管道

功能：
1. ETL流程：Extract → Transform → Load
2. 数据清洗和标准化
3. 数据质量检查
4. 增量更新处理
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import hashlib

@dataclass
class DataSchema:
    """数据模式定义"""
    name: str
    fields: Dict[str, str]  # 字段名 -> 类型
    required_fields: List[str]
    primary_key: List[str]
    timestamp_field: str

class DataPipeline:
    """数据管道"""
    
    # 标准数据模式定义
    SCHEMAS = {
        "price": DataSchema(
            name="price",
            fields={
                "symbol": "string",
                "date": "date",
                "open": "float",
                "high": "float",
                "low": "float",
                "close": "float",
                "volume": "int",
                "amount": "float",
                "change_pct": "float",
                "turnover": "float"
            },
            required_fields=["symbol", "date", "close"],
            primary_key=["symbol", "date"],
            timestamp_field="date"
        ),
        "financial": DataSchema(
            name="financial",
            fields={
                "symbol": "string",
                "report_date": "date",
                "report_type": "string",  # annual, quarterly
                "revenue": "float",
                "net_profit": "float",
                "eps": "float",
                "roe": "float",
                "debt_ratio": "float",
                "gross_margin": "float"
            },
            required_fields=["symbol", "report_date"],
            primary_key=["symbol", "report_date"],
            timestamp_field="report_date"
        ),
        "announcement": DataSchema(
            name="announcement",
            fields={
                "symbol": "string",
                "announce_date": "datetime",
                "title": "string",
                "content": "text",
                "type": "string",
                "source": "string",
                "url": "string"
            },
            required_fields=["symbol", "announce_date", "title"],
            primary_key=["symbol", "announce_date", "title"],
            timestamp_field="announce_date"
        ),
        "fund_flow": DataSchema(
            name="fund_flow",
            fields={
                "symbol": "string",
                "date": "date",
                "main_inflow": "float",
                "retail_inflow": "float",
                "institutional_inflow": "float",
                "net_inflow": "float"
            },
            required_fields=["symbol", "date"],
            primary_key=["symbol", "date"],
            timestamp_field="date"
        ),
        "sentiment": DataSchema(
            name="sentiment",
            fields={
                "symbol": "string",
                "date": "date",
                "sentiment_score": "float",  # -1 to 1
                "news_count": "int",
                "positive_count": "int",
                "negative_count": "int",
                "heat_score": "float"
            },
            required_fields=["symbol", "date"],
            primary_key=["symbol", "date"],
            timestamp_field="date"
        )
    }
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.raw_dir = f"{workspace}/data/architect_5l/raw_data"
        self.processed_dir = f"{workspace}/data/architect_5l/processed_data"
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 数据质量统计
        self._quality_stats = {}
    
    def extract(self, source: str, data: Any, metadata: Dict = None) -> Dict:
        """
        提取阶段：保存原始数据
        
        Args:
            source: 数据源名称
            data: 原始数据
            metadata: 元数据
        
        Returns:
            提取记录
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_id = hashlib.md5(f"{source}_{timestamp}_{str(data)}".encode()).hexdigest()[:12]
        
        record = {
            "data_id": data_id,
            "source": source,
            "extracted_at": datetime.now().isoformat(),
            "raw_data": data,
            "metadata": metadata or {}
        }
        
        # 保存原始数据
        raw_file = f"{self.raw_dir}/{source}_{timestamp}_{data_id}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        
        return record
    
    def transform(self, data: Dict, target_schema: str, 
                  transformations: List[Callable] = None) -> Dict:
        """
        转换阶段：清洗和标准化数据
        
        Args:
            data: 原始数据
            target_schema: 目标模式名称
            transformations: 自定义转换函数列表
        
        Returns:
            标准化数据
        """
        schema = self.SCHEMAS.get(target_schema)
        if not schema:
            raise ValueError(f"Unknown schema: {target_schema}")
        
        # 应用标准转换
        transformed = self._apply_standard_transforms(data, schema)
        
        # 应用自定义转换
        if transformations:
            for transform in transformations:
                transformed = transform(transformed)
        
        # 数据验证
        validation = self._validate_data(transformed, schema)
        transformed["_validation"] = validation
        
        return transformed
    
    def _apply_standard_transforms(self, data: Dict, schema: DataSchema) -> Dict:
        """应用标准转换"""
        result = {}
        
        for field, field_type in schema.fields.items():
            value = data.get(field)
            
            # 字段映射（处理不同数据源的字段名差异）
            if value is None:
                value = self._map_field(data, field)
            
            # 类型转换
            if value is not None:
                value = self._convert_type(value, field_type)
            
            result[field] = value
        
        # 添加元数据
        result["_processed_at"] = datetime.now().isoformat()
        result["_schema"] = schema.name
        
        return result
    
    def _map_field(self, data: Dict, target_field: str) -> Any:
        """字段映射"""
        # A股字段映射
        mappings = {
            "symbol": ["code", "stock_code", "ts_code", "股票代码"],
            "date": ["trade_date", "日期", "datetime", "时间"],
            "open": ["开盘价", "open_price"],
            "high": ["最高价", "high_price"],
            "low": ["最低价", "low_price"],
            "close": [["收盘价", "最新价"], "close_price", "price"],
            "volume": [["成交量", "vol"], "volume"],
            "amount": ["成交额", "amount"],
            "change_pct": [["涨跌幅", "pct_chg"], "change_percent", "change"]
        }
        
        alternatives = mappings.get(target_field, [])
        for alt in alternatives:
            if isinstance(alt, list):
                for a in alt:
                    if a in data:
                        return data[a]
            elif alt in data:
                return data[alt]
        
        return None
    
    def _convert_type(self, value: Any, target_type: str) -> Any:
        """类型转换"""
        try:
            if target_type == "float":
                return float(value) if value is not None else None
            elif target_type == "int":
                return int(float(value)) if value is not None else None
            elif target_type == "date":
                return self._parse_date(str(value))
            elif target_type == "datetime":
                return self._parse_datetime(str(value))
            elif target_type == "string":
                return str(value) if value is not None else None
            else:
                return value
        except:
            return None
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期"""
        formats = [
            "%Y-%m-%d",
            "%Y%m%d",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                continue
        
        return date_str
    
    def _parse_datetime(self, dt_str: str) -> str:
        """解析日期时间"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y%m%d%H%M%S",
            "%Y/%m/%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue
        
        return dt_str
    
    def _validate_data(self, data: Dict, schema: DataSchema) -> Dict:
        """验证数据"""
        errors = []
        warnings = []
        
        # 检查必填字段
        for field in schema.required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # 检查数据类型
        for field, value in data.items():
            if field.startswith("_"):
                continue
            
            expected_type = schema.fields.get(field)
            if expected_type and value is not None:
                if not self._check_type(value, expected_type):
                    warnings.append(f"Type mismatch for {field}: expected {expected_type}")
        
        # 检查数值范围
        if "close" in data and data["close"] is not None:
            if data["close"] <= 0:
                errors.append("Close price must be positive")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查类型"""
        if expected_type == "float":
            return isinstance(value, (int, float))
        elif expected_type == "int":
            return isinstance(value, int)
        elif expected_type == "string":
            return isinstance(value, str)
        elif expected_type in ["date", "datetime"]:
            return isinstance(value, str)
        return True
    
    def load(self, data: Dict, dataset: str) -> str:
        """
        加载阶段：保存处理后的数据
        
        Args:
            data: 处理后的数据
            dataset: 数据集名称
        
        Returns:
            保存的文件路径
        """
        symbol = data.get("symbol", "unknown")
        date = data.get("date", datetime.now().strftime("%Y%m%d"))
        
        # 构建保存路径
        dataset_dir = f"{self.processed_dir}/{dataset}"
        os.makedirs(dataset_dir, exist_ok=True)
        
        file_path = f"{dataset_dir}/{symbol}_{date}.json"
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def process(self, source: str, raw_data: Any, target_schema: str,
                dataset: str, metadata: Dict = None) -> Dict:
        """
        完整处理流程：Extract → Transform → Load
        
        Returns:
            处理结果
        """
        try:
            # Step 1: Extract
            extract_record = self.extract(source, raw_data, metadata)
            
            # Step 2: Transform
            transformed = self.transform(extract_record["raw_data"], target_schema)
            
            # Step 3: Load
            file_path = self.load(transformed, dataset)
            
            result = {
                "success": True,
                "data_id": extract_record["data_id"],
                "file_path": file_path,
                "schema": target_schema,
                "dataset": dataset,
                "validation": transformed.get("_validation", {}),
                "processed_at": datetime.now().isoformat()
            }
            
            # 更新质量统计
            self._update_quality_stats(target_schema, result["validation"])
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": source,
                "schema": target_schema,
                "processed_at": datetime.now().isoformat()
            }
    
    def _update_quality_stats(self, schema: str, validation: Dict):
        """更新质量统计"""
        if schema not in self._quality_stats:
            self._quality_stats[schema] = {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "errors": 0,
                "warnings": 0
            }
        
        stats = self._quality_stats[schema]
        stats["total"] += 1
        
        if validation.get("valid"):
            stats["valid"] += 1
        else:
            stats["invalid"] += 1
        
        stats["errors"] += validation.get("error_count", 0)
        stats["warnings"] += validation.get("warning_count", 0)
    
    def get_quality_report(self) -> Dict:
        """获取数据质量报告"""
        return self._quality_stats
    
    def generate_pipeline_report(self) -> str:
        """生成管道报告"""
        report = f"""# 📊 数据管道报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 数据质量统计

| 数据集 | 总数 | 有效 | 无效 | 错误数 | 警告数 |
|--------|------|------|------|--------|--------|
"""
        
        for schema, stats in self._quality_stats.items():
            valid_pct = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
            report += f"| {schema} | {stats['total']} | {stats['valid']} ({valid_pct:.1f}%) | {stats['invalid']} | {stats['errors']} | {stats['warnings']} |\n"
        
        report += """
---

## 📋 数据模式定义

"""
        
        for name, schema in self.SCHEMAS.items():
            report += f"""### {name}
- **字段数**: {len(schema.fields)}
- **必填字段**: {', '.join(schema.required_fields)}
- **主键**: {', '.join(schema.primary_key)}

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🔄 数据管道 (Layer 1)")
    print("=" * 70)
    
    pipeline = DataPipeline()
    
    # 演示数据
    sample_raw = {
        "code": "000001.SZ",
        "trade_date": "20260502",
        "开盘价": 10.5,
        "最高价": 10.8,
        "最低价": 10.3,
        "收盘价": 10.6,
        "成交量": 1000000,
        "成交额": 10600000,
        "涨跌幅": 0.95
    }
    
    print("\n📥 原始数据:")
    print(json.dumps(sample_raw, indent=2, ensure_ascii=False))
    
    # 处理流程
    print("\n🔄 执行ETL流程...")
    result = pipeline.process(
        source="akshare",
        raw_data=sample_raw,
        target_schema="price",
        dataset="daily_price",
        metadata={"market": "CN"}
    )
    
    print(f"\n✅ 处理结果:")
    print(f"  成功: {result['success']}")
    print(f"  数据ID: {result.get('data_id')}")
    print(f"  保存路径: {result.get('file_path')}")
    print(f"  验证状态: {'通过' if result.get('validation', {}).get('valid') else '失败'}")
    
    # 显示质量报告
    print("\n" + "=" * 70)
    print("📊 质量报告:")
    quality = pipeline.get_quality_report()
    print(json.dumps(quality, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
