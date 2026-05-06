# A5L Alpha测试 - 快速启动指南

## 🚀 明日启动步骤 (2026-05-05 09:00)

### 一键启动
```bash
cd /workspace/projects/workspace
./start_alpha_test.sh
```

### 手动步骤 (如果一键启动失败)

#### Step 1: 环境检查 (2分钟)
```bash
cd /workspace/projects/workspace
python3 --version  # 确认Python3正常
git status         # 确认Git状态正常
```

#### Step 2: 系统健康检查 (1分钟)
```bash
python3 test_system_health.py
# 期望输出: 100/100 健康评分
```

#### Step 3: 运行自动化测试 (2分钟)
```bash
python3 test_alpha_suite.py
# 期望输出: 15/15 测试通过
```

#### Step 4: 备份配置 (30秒)
```bash
mkdir -p backups/$(date +%Y%m%d)
cp -r data/positions backups/$(date +%Y%m%d)/
echo "备份完成"
```

#### Step 5: 启动Alpha测试 (1分钟)
```bash
mkdir -p logs/alpha_test
echo "$(date): Alpha test started" > logs/alpha_test/system.log
./start_alpha.sh
```

#### Step 6: 验证启动 (30秒)
```bash
./monitor_alpha.sh
# 期望看到: ✅ Alpha测试进程运行中
```

---

## 📊 今日检查清单 (Day 1)

### 09:00 - 启动检查
- [ ] 执行启动脚本
- [ ] 验证系统健康 100/100
- [ ] 验证15个测试通过
- [ ] 确认日志正常生成

### 10:00 - 首次监控
- [ ] 运行 ./monitor_alpha.sh
- [ ] 检查日志无错误
- [ ] 确认数据流正常

### 12:00 - 午间检查
- [ ] 检查系统运行状态
- [ ] 记录任何异常

### 15:00 - 下午检查
- [ ] A股收盘检查
- [ ] 确认当日无交易错误

### 21:00 - 晚间检查
- [ ] 美股监控启动
- [ ] 生成首日日报
- [ ] 总结Day 1问题

### 23:00 - 日终检查
- [ ] 确认系统稳定运行
- [ ] 备份当日日志
- [ ] 准备Day 2计划

---

## 🆘 应急处理

### 场景1: 系统崩溃
```bash
# 1. 立即停止
pkill -f alpha

# 2. 保存日志
cp logs/alpha_test/system.log backups/crash_$(date +%Y%m%d_%H%M%S).log

# 3. 分析原因
 tail -100 logs/alpha_test/system.log

# 4. 修复后重启
./start_alpha_test.sh
```

### 场景2: 数据异常
```bash
# 1. 暂停交易
# (修改配置文件 trading.enabled = false)

# 2. 检查数据一致性
python3 TOOLS/data_consistency_checker.py

# 3. 修复数据
python3 TOOLS/p0_data_consistency_fix.py

# 4. 恢复交易
# (修改配置文件 trading.enabled = true)
```

### 场景3: 测试失败
```bash
# 1. 运行测试查看详情
python3 test_alpha_suite.py -v

# 2. 记录失败的测试
# 3. 修复问题
# 4. 重新运行测试
```

---

## 📞 联系支持

| 问题类型 | 处理人 | 响应时间 |
|----------|--------|----------|
| 系统崩溃 | Chief Architect | 5分钟 |
| 数据异常 | Data Engineer | 15分钟 |
| 策略问题 | CIO | 30分钟 |
| 风控告警 | CSO | 立即 |

---

## 📝 每日记录模板

```markdown
## Alpha测试 Day X - 2026-05-XX

### 系统状态
- 运行时间: XX小时
- 健康状况: [正常/警告/异常]
- 异常情况: [无/描述]

### 测试进展
- 当前Phase: X
- 完成用例: XX/XX
- 发现问题: X个

### 交易表现
- 日收益: X.XX%
- 累计收益: X.XX%
- 最大回撤: X.XX%

### 明日计划
- [ ] 任务1
- [ ] 任务2
```

---

**Alpha测试明天正式启动！准备好开始了吗？** 🚀
