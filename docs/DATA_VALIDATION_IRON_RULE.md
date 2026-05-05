# A5L 数据校验铁律 v1.0

**版本**: v1.0  
**生效日期**: 2026-05-05  
**核心原则**: **虚假数据零容忍，校验失败即停止**

---

## 一、数据校验五层防线

### Layer 1: 源头校验（Data Engineer）
**负责人**: Data Engineer Agent  
**校验时机**: 数据采集时（实时）  
**校验内容**:
```python
def validate_source_data(raw_data):
    checks = {
        "price_range": 0 < price < 100000,  # 股价不能为0或负数，不能离谱
        "volume_positive": volume >= 0,      # 成交量不能为负
        "change_limit": -0.3 < change_pct < 0.3,  # A股涨跌幅限制±30%
        "timestamp_valid": is_trading_time(timestamp),  # 时间戳在交易时段
        "data_fresh": now - timestamp < 600,  # 数据延迟<10分钟
    }
    return all(checks.values())
```

**失败处理**:
- ❌ 任一检查失败 → 标记数据源为unreliable
- ❌ 切换到备用数据源（AKShare → TuShare → Yahoo）
- ❌ 记录失败日志，报告给CSO

---

### Layer 2: 交叉验证（CIO）
**负责人**: CIO Agent  
**校验时机**: 数据进入分析流程前  
**校验内容**:
```python
def cross_validate(indicator, sources):
    """多数据源交叉验证"""
    values = [s.get(indicator) for s in sources]
    
    # 1. 离群值检测（3σ原则）
    mean = np.mean(values)
    std = np.std(values)
    outliers = [v for v in values if abs(v - mean) > 3 * std]
    
    # 2. 一致性检查
    max_diff = max(values) - min(values)
    consistency = max_diff / mean if mean != 0 else float('inf')
    
    return {
        "valid": len(outliers) == 0 and consistency < 0.05,  # 差异<5%
        "confidence": calculate_confidence(values),
        "outliers": outliers
    }
```

**关键指标交叉验证**:
- 股价: AKShare vs TuShare vs 雪球
- 涨跌幅: 手动计算 vs API返回
- 市值: 股价 × 股本 vs API返回市值
- 北向资金: 东方财富 vs 同花顺

**失败处理**:
- ❌ 差异>5% → 标记为questionable，降低置信度
- ❌ 差异>10% → 拒绝使用该数据，告警CSO

---

### Layer 3: 逻辑校验（A5L Layer 3）
**负责人**: A5L Layer 3（多SKILL交叉）  
**校验时机**: 分析生成时  
**校验内容**:
```python
def logic_validate(skill_outputs):
    """多SKILL输出逻辑一致性检查"""
    
    # 1. 方向一致性
    directions = {
        "langzhu": skill_outputs['langzhu']['direction'],  # 看多/看空/观望
        "buffett": skill_outputs['buffett']['sentiment'],   # 贪婪/恐惧/中性
        "factor": skill_outputs['factor']['style']          # 成长/价值/均衡
    }
    
    # 检查矛盾（如浪主看多 + 巴菲特极度恐慌）
    contradictions = detect_contradictions(directions)
    
    # 2. 数值合理性
    checks = {
        "buffett_score": 0 <= skill_outputs['buffett']['score'] <= 100,
        "浪主_days": 1 <= skill_outputs['langzhu']['day_count'] <= 20,
        "uzi_score": 0 <= skill_outputs['uzi']['score'] <= 100,
    }
    
    return {
        "consistent": len(contradictions) == 0,
        "contradictions": contradictions,
        "valid": all(checks.values())
    }
```

**矛盾示例**:
- ❌ 浪主指数: 反弹第5天（看多） + 巴菲特情绪: 15分（极度恐慌）
- ❌ UZI评分: 90分（强烈推荐） + 空方视角: 5个重大风险

**失败处理**:
- ❌ 发现矛盾 → 标注置信度降低，报告给Chief
- ❌ 严重矛盾 → 暂停生成建议，人工确认

---

### Layer 4: 持仓数据铁律（CSO - 最关键）
**负责人**: CSO Agent  
**校验时机**: 接收到Chief截图时 + 生成日报前  
**核心原则**: **截图数据是唯一真理**

#### 4.1 截图OCR校验流程
```python
def validate_position_data(screenshot_data, system_data):
    """
    截图数据 vs 系统数据强制对齐
    """
    discrepancies = []
    
    for account in ['张晋', '王力', 'WGB', '老娘']:
        # 1. 持仓股票代码必须一致
        if screenshot_data[account]['stocks'] != system_data[account]['stocks']:
            discrepancies.append(f"{account}: 持仓股票不一致")
        
        # 2. 持仓数量差异<1%（允许OCR误差）
        for stock in screenshot_data[account]['stocks']:
            ss_qty = screenshot_data[account]['positions'][stock]['quantity']
            sys_qty = system_data[account]['positions'][stock]['quantity']
            
            if abs(ss_qty - sys_qty) / ss_qty > 0.01:  # 差异>1%
                discrepancies.append(f"{account}.{stock}: 数量不一致 ({ss_qty} vs {sys_qty})")
        
        # 3. 成本价差异<2%（允许OCR误差）
        for stock in screenshot_data[account]['stocks']:
            ss_cost = screenshot_data[account]['positions'][stock]['cost']
            sys_cost = system_data[account]['positions'][stock]['cost']
            
            if abs(ss_cost - sys_cost) / ss_cost > 0.02:  # 差异>2%
                discrepancies.append(f"{account}.{stock}: 成本不一致 ({ss_cost} vs {sys_cost})")
    
    return {
        "valid": len(discrepancies) == 0,
        "discrepancies": discrepancies,
        "screenshot_priority": True  # 截图数据优先
    }
```

#### 4.2 担保比例独立计算
```python
def calculate_margin_ratio(account_data):
    """
    独立计算担保比例，不依赖券商数据
    """
    total_assets = account_data['cash'] + account_data['market_value']
    total_liabilities = account_data['margin_loan'] + account_data['interest_payable']
    
    margin_ratio = (total_assets / total_liabilities) * 100 if total_liabilities > 0 else float('inf')
    
    # 双重校验：用另一种方法计算
    alt_calc = (account_data['total_equity'] / account_data['margin_used']) * 100
    
    # 两种方法差异必须<2%
    if abs(margin_ratio - alt_calc) > 2:
        return {"valid": False, "error": "担保比例计算不一致", "values": [margin_ratio, alt_calc]}
    
    return {"valid": True, "margin_ratio": margin_ratio}
```

#### 4.3 持仓数据铁律
```
┌─────────────────────────────────────────────────────────────┐
│                    CSO持仓数据铁律                          │
├─────────────────────────────────────────────────────────────┤
│  1. 所有持仓数据必须以Chief提供的截图为唯一准               │
│  2. 系统记录与截图不一致时，以截图为准，系统记录标记为待修正 │
│  3. 担保比例必须独立计算，双重验证                          │
│  4. 发现数据异常立即告警，暂停交易建议                      │
│  5. 每日截图到达后15分钟内完成OCR校验和比对                 │
└─────────────────────────────────────────────────────────────┘
```

**失败处理（零容忍）**:
- 🚨 截图与系统数据不一致 → 以截图为准，系统数据标记为questionable
- 🚨 担保比例计算不一致 → 立即告警Chief，暂停杠杆建议
- 🚨 OCR识别失败 → 请求Chief重新发送截图，暂停该账户分析

---

### Layer 5: 最终输出校验（Report Manager）
**负责人**: Report Manager Agent  
**校验时机**: 日报生成后，发送前  
**校验内容**:
```python
def final_validate(report):
    """日报最终校验"""
    
    checks = {
        # 1. 完整性检查
        "all_sections_present": all(section in report for section in REQUIRED_SECTIONS),
        
        # 2. 数据一致性
        "market_data_consistent": report['market']['sh_close'] > 0,
        "position_data_complete": len(report['positions']) == 4,  # 4个账户
        "pnl_calculations_correct": validate_pnl_math(report['positions']),
        
        # 3. 逻辑一致性
        "recommendations_match_analysis": check_recommendation_consistency(report),
        "risk_warnings_appropriate": check_risk_warnings(report),
        
        # 4. 可溯源性
        "all_numbers_traceable": all(has_data_source(num) for num in report['numbers']),
        "skill_calls_logged": len(report['skill_calls']) == 37,
    }
    
    return {
        "valid": all(checks.values()),
        "failed_checks": [k for k, v in checks.items() if not v],
        "confidence_score": calculate_overall_confidence(report)
    }
```

**失败处理**:
- ❌ 完整性检查失败 → 回滚重生成，记录错误
- ❌ 数据不一致 → 标记questionable，降低置信度
- ❌ 逻辑不一致 → 暂停发送，人工审核

---

## 二、数据质量评分体系

### 日报数据质量评分（0-100分）
```python
def calculate_data_quality_score(report):
    """计算日报数据质量评分"""
    
    scores = {
        "source_reliability": 30,    # 数据源可靠性（30分）
        "cross_validation": 25,       # 交叉验证通过率（25分）
        "logic_consistency": 20,      # 逻辑一致性（20分）
        "position_accuracy": 20,      # 持仓数据准确性（20分）- 最重要
        "completeness": 5,            # 完整性（5分）
    }
    
    # 持仓数据零容忍
    if not report['validation']['position_data_valid']:
        scores['position_accuracy'] = 0
        report['quality_level'] = "UNRELIABLE"
        report['action'] = "STOP_AND_ALERT"
    
    total_score = sum(scores.values())
    
    # 质量等级
    if total_score >= 90:
        level = "EXCELLENT"
    elif total_score >= 80:
        level = "GOOD"
    elif total_score >= 70:
        level = "ACCEPTABLE"
    elif total_score >= 60:
        level = "QUESTIONABLE"
    else:
        level = "UNRELIABLE"
        action = "DO_NOT_SEND"
    
    return {"score": total_score, "level": level, "breakdown": scores}
```

### 日报输出格式
```
═══════════════════════════════════════════════════════════════════
数据质量评分: 85/100 (GOOD) ✅
持仓数据校验: PASS ✅ | 交叉验证: 4/5 ⚠️ | 逻辑一致性: PASS ✅
═══════════════════════════════════════════════════════════════════
```

---

## 三、数据异常响应流程

### 分级响应机制

**Level 1: 轻微异常**（质量评分70-79）
- 处理: 标注questionable，降低置信度，正常发送
- 通知: 记录日志，不主动告警
- 示例: 某个SKILL输出置信度较低

**Level 2: 中度异常**（质量评分60-69）
- 处理: 标注questionable，暂停相关建议
- 通知: 告警CSO，Chief知悉
- 示例: 持仓数据OCR识别率<95%

**Level 3: 严重异常**（质量评分<60 或 持仓数据错误）
- 处理: 🚨 立即停止生成日报，暂停交易建议
- 通知: 🚨 紧急告警Chief和CSO
- 行动: 人工介入，查明原因，修正数据
- 示例: 截图与系统数据严重不符、担保比例计算错误

---

## 四、责任矩阵

| 层级 | 责任人 | 校验内容 | 失败处理 | 问责 |
|------|--------|----------|----------|------|
| Layer 1 | Data Engineer | 数据源有效性 | 切换备用源 | Data Engineer修复 |
| Layer 2 | CIO | 交叉验证 | 标记questionable | CIO修复计算 |
| Layer 3 | A5L L3 | 逻辑一致性 | 降低置信度 | CA审核 |
| Layer 4 | CSO | 持仓数据准确性 | 🚨 立即停止 | CSO立即修正 |
| Layer 5 | Report Manager | 最终输出完整性 | 回滚重生成 | Report Manager修复 |

---

## 五、执行检查清单

### 每日执行（17:30日报生成前）
- [ ] Data Engineer: 所有数据源API正常
- [ ] Data Engineer: 关键指标交叉验证通过
- [ ] CSO: 收到Chief截图并完成OCR
- [ ] CSO: 截图数据与系统记录比对完成
- [ ] CSO: 担保比例独立计算验证
- [ ] A5L L3: 多SKILL输出一致性检查
- [ ] Report Manager: 最终输出完整性检查
- [ ] Report Manager: 数据质量评分≥70分

### 任何一层失败即停止，直至修正完成

---

## 六、承诺

**我，CA（Chief Architect），承诺：**

1. 数据准确性是A5L的生命线，虚假数据零容忍
2. 五层校验防线严格执行，任何一层失败即停止
3. 持仓数据以截图为准，OCR校验是强制流程
4. 发现数据问题立即告警，绝不隐瞒或敷衍
5. 持续优化校验流程，不断提高数据质量

**此铁律自2026-05-05起生效，违反者问责。**

---

*制定: CA (Chief Architect)*  
*审核: CSO (Chief Security Officer)*  
*批准: Chief (张晋)*  
*生效: 2026-05-05*
