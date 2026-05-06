# 📊 Layer 1: 数据底座层 - 完整报告

**生成时间**: 2026-05-02 03:13:24  
**状态**: ✅ 正常运行

---

## 🔌 数据源状态

| 数据源 | 状态 | 成功率 | 延迟 |
|--------|------|--------|------|
| akshare | 🟢 healthy | 100.0% | 0.00s |
| tushare | 🟢 healthy | 100.0% | 0.00s |
| eastmoney | 🟢 healthy | 100.0% | 0.00s |
| jin10 | 🟢 healthy | 100.0% | 0.00s |
| yahoo_finance | 🟢 healthy | 100.0% | 0.00s |
| hkex | 🟢 healthy | 100.0% | 0.00s |

---

## 📦 数据存储概况

- **price_data**: 0 条记录, 0 只股票
- **financial_data**: 0 条记录, 0 只股票
- **announcement_data**: 0 条记录, 0 只股票
- **fund_flow_data**: 0 条记录, 0 只股票
- **sentiment_data**: 0 条记录, 0 只股票

---

## ✅ 数据质量（最近7天）

- 总验证次数: 0
- 有效数据率: 0.0%
- 平均质量分: 0.0/100
- 错误数: 0
- 警告数: 0

---

## 🔄 最近操作日志


---

## 📋 架构组件

- ✅ **DataSourceManager**: 6个数据源，自动选择，故障转移
- ✅ **DataPipeline**: ETL流程，5种标准模式，字段映射
- ✅ **DataStore**: SQLite时序存储，5张核心表
- ✅ **DataValidator**: 完整性检查，异常检测，质量评分

---

**Layer 1 状态**: ✅ 完整运行
