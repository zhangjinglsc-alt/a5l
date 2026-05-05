# CA规划：CTO SKILL执行与能力开发方案
**规划者**: Chief Architect (CA)  
**执行者**: CTO  
**时间**: 2026-05-06  
**目标**: 建立完整代码工程能力体系

---

## 📋 现状评估

### 已部署P0系统 (✅ 完成)
| 系统 | 状态 | 配置位置 |
|:-----|:----:|:---------|
| Upptime | ✅ 配置完成 | `monitoring/upptime/` |
| Wolverine | ✅ 已安装 | `monitoring/wolverine/a5l_wolverine.py` |
| Prometheus | ✅ 配置完成 | `monitoring/prometheus/` |

### CTO能力差距
| 能力域 | 当前 | 目标 | 缺口 |
|:-------|:----:|:----:|:----:|
| 自愈自动化 | ⭐ | ⭐⭐⭐⭐⭐ | 4级 |
| 监控告警 | ⭐ | ⭐⭐⭐⭐⭐ | 4级 |
| DevOps/SRE | ⭐ | ⭐⭐⭐⭐⭐ | 4级 |
| 系统架构 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 3级 |

---

## 🎯 CA规划方案

### 阶段一：P0系统激活 (立即执行)

#### 任务1: 激活Upptime状态监控
**执行者**: CTO  
**时间**: 30分钟  
**步骤**:
```bash
# 1. 在GitHub创建新仓库: a5l-upptime
# 2. 复制配置文件
cp -r monitoring/upptime/* ~/a5l-upptime/

# 3. 设置GitHub Secrets
echo "Settings → Secrets → New repository secret"
echo "Name: GH_PAT"
echo "Value: [GitHub Personal Access Token]"
echo ""
echo "Name: FEISHU_WEBHOOK_URL"  
echo "Value: [飞书机器人Webhook]"

# 4. 启用GitHub Actions
echo "Actions → Enable workflows"

# 5. 验证
open https://[username].github.io/a5l-upptime
```

**交付物**: 可访问的状态页面 + 飞书告警

---

#### 任务2: 配置Prometheus + Grafana
**执行者**: CTO  
**时间**: 1小时  
**步骤**:
```bash
# 1. 下载安装Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
sudo mv prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/

# 2. 启动Prometheus
prometheus \
  --config.file=/workspace/projects/workspace/monitoring/prometheus/prometheus.yml \
  --storage.tsdb.path=/tmp/prometheus \
  --web.console.templates=/usr/local/bin/consoles \
  --web.console.libraries=/usr/local/bin/console_libraries

# 3. 安装Grafana
sudo apt-get install -y grafana
sudo systemctl start grafana-server

# 4. 配置数据源
open http://localhost:3000 (admin/admin)
echo "Configuration → Data Sources → Add Prometheus"
echo "URL: http://localhost:9090"

# 5. 导入Dashboard
# 上传 monitoring/grafana/dashboards/a5l-dashboard.json
```

**交付物**: Prometheus仪表盘 + Grafana可视化

---

#### 任务3: 配置Alertmanager飞书通知
**执行者**: CTO  
**时间**: 45分钟  
**步骤**:
```bash
# 1. 安装Alertmanager
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
tar xvfz alertmanager-0.26.0.linux-amd64.tar.gz
sudo mv alertmanager-0.26.0.linux-amd64/alertmanager /usr/local/bin/

# 2. 创建配置
cat > /workspace/projects/workspace/monitoring/prometheus/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@a5l.local'

route:
  receiver: 'feishu-webhook'
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'feishu-webhook'
    webhook_configs:
      - url: '${FEISHU_WEBHOOK_URL}'
        send_resolved: true
EOF

# 3. 启动Alertmanager
alertmanager \
  --config.file=/workspace/projects/workspace/monitoring/prometheus/alertmanager.yml \
  --storage.path=/tmp/alertmanager

# 4. 测试告警
curl -X POST http://localhost:9093/-/reload
```

**交付物**: 飞书实时告警

---

### 阶段二：SKILL能力开发 (本周内)

#### 任务4: 建立自愈规则库
**执行者**: CTO  
**时间**: 2天  
**目标**: 开发A5L专属自愈规则

**文件**: `monitoring/wolverine/healing_rules.py`
```python
#!/usr/bin/env python3
"""
A5L 自愈规则库
定义常见错误的自动修复策略
"""

HEALING_RULES = {
    # 数据源切换
    "yahoo_rate_limit": {
        "pattern": "Too Many Requests",
        "action": "switch_to_finnhub",
        "description": "Yahoo Finance限流时自动切换到Finnhub"
    },
    
    # API Key失效
    "api_key_invalid": {
        "pattern": "Invalid API key",
        "action": "rotate_api_key",
        "description": "API Key失效时自动轮换"
    },
    
    # 持仓数据异常
    "position_data_corrupt": {
        "pattern": "JSON parse error",
        "action": "restore_from_backup",
        "description": "持仓数据损坏时从备份恢复"
    },
    
    # 飞书文档更新失败
    "feishu_doc_update_failed": {
        "pattern": "forbidden.*1770032",
        "action": "recreate_document",
        "description": "飞书文档更新失败时重新创建"
    },
    
    # GitHub推送失败
    "github_push_failed": {
        "pattern": "Push failed",
        "action": "retry_with_delay",
        "description": "GitHub推送失败时重试"
    },
    
    # 内存不足
    "memory_error": {
        "pattern": "MemoryError|out of memory",
        "action": "clear_cache",
        "description": "内存不足时清理缓存"
    }
}

class HealingExecutor:
    """自愈执行器"""
    
    def execute(self, rule_name: str, context: dict) -> bool:
        """执行指定自愈规则"""
        rule = HEALING_RULES.get(rule_name)
        if not rule:
            return False
        
        action = rule["action"]
        method = getattr(self, f"_action_{action}")
        return method(context)
    
    def _action_switch_to_finnhub(self, context):
        """切换到Finnhub数据源"""
        from tools.unified_data_source_manager import DataSourceManager
        dm = DataSourceManager()
        dm.switch_primary("finnhub")
        return True
    
    def _action_clear_cache(self, context):
        """清理缓存"""
        import shutil
        cache_dirs = ['/tmp/a5l_cache', '/tmp/openclaw']
        for d in cache_dirs:
            if os.path.exists(d):
                shutil.rmtree(d)
        return True
    
    def _action_restore_from_backup(self, context):
        """从备份恢复"""
        # 执行三重备份恢复
        os.system("python3 TOOLS/ssmg_restore.py")
        return True
```

**交付物**: 6条自愈规则 + 执行器框架

---

#### 任务5: 开发预测性维护模块
**执行者**: CTO  
**时间**: 3天  
**目标**: 基于历史数据预测系统故障

**文件**: `monitoring/predictive/maintenance_predictor.py`
```python
#!/usr/bin/env python3
"""
A5L 预测性维护系统
基于历史指标预测未来故障
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import List, Dict

class MaintenancePredictor:
    """
    预测性维护预测器
    使用统计方法预测系统健康趋势
    """
    
    def __init__(self):
        self.metrics_history = []
        self.load_history()
    
    def predict_disk_full(self, days: int = 7) -> Dict:
        """预测磁盘满载时间"""
        # 基于历史增长率预测
        if len(self.metrics_history) < 3:
            return {"predicted": None, "confidence": 0}
        
        disk_usage = [m["disk_percent"] for m in self.metrics_history[-30:]]
        if len(disk_usage) < 2:
            return {"predicted": None, "confidence": 0}
        
        # 计算增长率
        growth_rate = (disk_usage[-1] - disk_usage[0]) / len(disk_usage)
        
        if growth_rate <= 0:
            return {"predicted": None, "confidence": 0.9, "note": "磁盘使用稳定"}
        
        # 预测达到90%的天数
        current = disk_usage[-1]
        days_to_full = (90 - current) / growth_rate
        
        predicted_date = datetime.now() + timedelta(days=days_to_full)
        
        return {
            "predicted": predicted_date.isoformat(),
            "days_remaining": days_to_full,
            "confidence": min(0.95, 0.5 + 0.1 * len(disk_usage)),
            "current_usage": current,
            "growth_rate_per_day": growth_rate
        }
    
    def predict_api_rate_limit(self, api_name: str) -> Dict:
        """预测API限流风险"""
        # 基于请求频率预测
        request_counts = self.get_api_request_counts(api_name)
        
        if not request_counts:
            return {"risk": "unknown"}
        
        avg_requests = statistics.mean(request_counts)
        max_requests = max(request_counts)
        
        # 假设限制为1000/小时
        limit = 1000
        utilization = avg_requests / limit
        
        if utilization > 0.9:
            return {"risk": "high", "utilization": utilization, "action": "reduce_frequency"}
        elif utilization > 0.7:
            return {"risk": "medium", "utilization": utilization, "action": "monitor"}
        else:
            return {"risk": "low", "utilization": utilization}
    
    def generate_maintenance_schedule(self) -> List[Dict]:
        """生成维护计划"""
        schedule = []
        
        # 磁盘维护
        disk_prediction = self.predict_disk_full()
        if disk_prediction.get("days_remaining", 999) < 7:
            schedule.append({
                "type": "disk_cleanup",
                "priority": "high",
                "due_date": disk_prediction["predicted"],
                "reason": f"磁盘将在{disk_prediction['days_remaining']:.1f}天后达到90%"
            })
        
        # API维护
        for api in ["yahoo", "finnhub", "tushare"]:
            risk = self.predict_api_rate_limit(api)
            if risk.get("risk") == "high":
                schedule.append({
                    "type": "api_optimization",
                    "priority": "medium", 
                    "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "reason": f"{api} API使用率过高"
                })
        
        return sorted(schedule, key=lambda x: x["priority"])
```

**交付物**: 预测性维护引擎 + 维护计划生成

---

### 阶段三：集成方案 (整体架构)

#### 架构图
```
┌─────────────────────────────────────────────────────────────────┐
│                    A5L 监控自愈体系 (CA设计)                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: 感知层                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Upptime    │  │ Prometheus  │  │  A5L内置    │             │
│  │  (状态监控)  │  │  (指标采集)  │  │  (业务监控)  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         └─────────────────┼─────────────────┘                    │
│                           ▼                                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: 告警层                                                 │
│  ┌─────────────────────────────────────────────────┐             │
│  │              Alertmanager                        │             │
│  │    ┌──────────┬──────────┬──────────┐          │             │
│  │    │ 飞书通知 │ 邮件通知 │ 页面展示 │          │             │
│  │    └──────────┴──────────┴──────────┘          │             │
│  └─────────────────────────────────────────────────┘             │
│                           │                                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: 自愈层 (CTO开发)                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 错误分类器  │→│ 规则匹配器  │→│ 执行器      │             │
│  │(Error Class)│  │(Rule Match) │  │(Healing Exec)│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         ↑                                               │       │
│         └───────────────────────────────────────────────┘       │
│                           │                                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: 预测层 (CTO开发)                                       │
│  ┌─────────────────────────────────────────────────┐             │
│  │         MaintenancePredictor                     │             │
│  │    • 磁盘满载预测                                │             │
│  │    • API限流预测                                 │             │
│  │    • 维护计划生成                                │             │
│  └─────────────────────────────────────────────────┘             │
│                           │                                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5: 可视化层                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Grafana   │  │  状态页面   │  │   报告      │             │
│  │  (仪表盘)   │  │  (Upptime)  │  │  (日报)     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 能力开发路线图

### CTO技能成长路径

| 阶段 | 时间 | 目标 | 学习资源 |
|:-----|:-----|:-----|:---------|
| **初级** | 1-2周 | 掌握Prometheus+Grafana基础 | Prometheus官方文档 |
| **中级** | 3-4周 | 开发自愈规则 + 告警配置 | SRE Google书籍 |
| **高级** | 1-2月 | 预测性维护 + 混沌工程 | Netflix Chaos Engineering |
| **专家** | 3-6月 | 完整SRE体系 + 自动化运维 | Kubernetes + GitOps |

### 必备技能清单

```yaml
SRE核心技能:
  - 监控体系设计 (Prometheus/Grafana)
  - 告警管理 (Alertmanager/PagerDuty)
  - 日志分析 (ELK/Loki)
  - 故障排查 (Linux/Network)
  
DevOps技能:
  - CI/CD (GitHub Actions/GitLab CI)
  - 容器化 (Docker/Kubernetes)
  - 基础设施即代码 (Terraform/Ansible)
  
编程能力:
  - Python (自动化脚本)
  - Go (高性能工具)
  - Shell (系统管理)
  
软技能:
  - 故障复盘 (Post-mortem)
  - 容量规划 (Capacity Planning)
  - 应急响应 (Incident Response)
```

---

## 🚀 执行命令

### CTO立即执行 (按顺序)

```bash
# ===== 阶段一: P0系统激活 =====

# 1. 创建GitHub仓库并激活Upptime
echo "Step 1: 激活Upptime状态监控..."
cd ~/a5l-upptime
git init
git add .
git commit -m "Initial Upptime config"
git push origin main
echo "✅ Upptime已激活"

# 2. 启动Prometheus
echo "Step 2: 启动Prometheus..."
prometheus \
  --config.file=/workspace/projects/workspace/monitoring/prometheus/prometheus.yml \
  --storage.tsdb.path=/tmp/prometheus &
echo "✅ Prometheus运行在 http://localhost:9090"

# 3. 启动Alertmanager
echo "Step 3: 启动Alertmanager..."
alertmanager \
  --config.file=/workspace/projects/workspace/monitoring/prometheus/alertmanager.yml &
echo "✅ Alertmanager运行在 http://localhost:9093"

# 4. 验证监控
open http://localhost:9090/targets
echo "检查所有target状态是否为UP"

# ===== 阶段二: SKILL开发 =====

echo "Step 5: 开发自愈规则库..."
cd /workspace/projects/workspace
touch monitoring/wolverine/healing_rules.py
# [按上述规范编写代码]

echo "Step 6: 开发预测性维护..."
touch monitoring/predictive/maintenance_predictor.py
# [按上述规范编写代码]

echo "✅ 所有任务完成！"
```

---

## 📊 交付检查清单

### 阶段一交付 (本周五前)
- [ ] Upptime状态页面可访问
- [ ] Prometheus采集所有目标
- [ ] Grafana仪表盘显示数据
- [ ] 飞书收到测试告警

### 阶段二交付 (下周五前)
- [ ] 自愈规则库完成6条规则
- [ ] 预测性维护模块可预测磁盘/API
- [ ] 自动生成维护计划
- [ ] 集成到A5L主系统

---

## 🎯 成功标准

| 指标 | 目标 | 验证方式 |
|:-----|:-----|:---------|
| 监控覆盖率 | 100% | 所有服务都有监控 |
| 告警响应时间 | < 5分钟 | 模拟故障测试 |
| 自愈成功率 | > 80% | 统计自愈记录 |
| 预测准确率 | > 70% | 对比预测vs实际 |
| MTTR | < 30分钟 | 平均修复时间 |

---

**CA签名**: Chief Architect  
**日期**: 2026-05-06  
**状态**: 🟡 规划中，待CTO执行
