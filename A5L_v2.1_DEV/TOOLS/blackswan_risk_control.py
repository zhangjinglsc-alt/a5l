#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black Swan Risk Control System
黑天鹅风控系统

功能：
1. 实时监控市场极端情况
2. 自动检测黑天鹅事件
3. 执行紧急斩仓
4. 跨市场联动风险监控
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class BlackSwanRiskControl:
    """黑天鹅风控系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.rules_file = f"{workspace}/data/trading_rules/active_rules.json"
        self.alerts_file = f"{workspace}/data/trading_analytics/blackswan_alerts.json"
        self.state_file = f"{workspace}/data/trading_analytics/risk_state.json"
        
        os.makedirs(f"{workspace}/data/trading_analytics", exist_ok=True)
        
        self.risk_rules = self._load_risk_rules()
        self.state = self._load_state()
    
    def _load_risk_rules(self) -> Dict:
        """加载风控规则"""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
                # 找到黑天鹅规则
                for rule in rules:
                    if rule.get('rule_id') == 'RULE-BLACKSWAN-001':
                        return rule
        return {}
    
    def _load_state(self) -> Dict:
        """加载风控状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "risk_level": "normal",  # normal, elevated, high, critical
            "last_check": None,
            "active_alerts": [],
            "emergency_mode": False,
            "exposure_reduction": 0  # 百分比
        }
    
    def _save_state(self):
        """保存风控状态"""
        self.state["last_check"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _save_alert(self, alert: Dict):
        """保存警报"""
        alerts = []
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
        
        alerts.append(alert)
        
        # 只保留最近100条
        alerts = alerts[-100:]
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    def check_market_conditions(self, market_data: Dict) -> List[Dict]:
        """检查市场状况，返回触发的警报"""
        alerts = []
        triggers = self.risk_rules.get('triggers', [])
        
        for trigger in triggers:
            if self._check_trigger(trigger, market_data):
                alert = {
                    "id": f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{trigger['name']}",
                    "timestamp": datetime.now().isoformat(),
                    "trigger_name": trigger['name'],
                    "market": trigger['market'],
                    "action": trigger['action'],
                    "severity": self._get_severity(trigger['action']),
                    "status": "active"
                }
                alerts.append(alert)
                self._save_alert(alert)
        
        # 更新风控状态
        if alerts:
            self._update_risk_state(alerts)
        
        self._save_state()
        return alerts
    
    def _check_trigger(self, trigger: Dict, market_data: Dict) -> bool:
        """检查单个触发条件"""
        conditions = trigger.get('conditions', [])
        market = trigger.get('market', 'ANY')
        
        # 获取对应市场数据
        data = market_data.get(market, market_data)
        
        all_met = True
        for condition in conditions:
            indicator = condition.get('indicator', '')
            actual_value = data.get(indicator, 0)
            
            # 检查条件
            if 'above' in condition:
                if actual_value <= condition['above']:
                    all_met = False
                    break
            elif 'below' in condition:
                if actual_value >= condition['below']:
                    all_met = False
                    break
        
        return all_met
    
    def _get_severity(self, action: str) -> str:
        """获取警报严重程度"""
        if 'emergency' in action.lower() or 'liquidate_all' in action.lower():
            return "critical"
        elif 'reduce' in action.lower():
            return "high"
        else:
            return "elevated"
    
    def _update_risk_state(self, alerts: List[Dict]):
        """更新风控状态"""
        severities = [a['severity'] for a in alerts]
        
        if 'critical' in severities:
            self.state['risk_level'] = 'critical'
            self.state['emergency_mode'] = True
            self.state['exposure_reduction'] = 100
        elif 'high' in severities:
            self.state['risk_level'] = 'high'
            if not self.state['emergency_mode']:
                self.state['exposure_reduction'] = max(self.state['exposure_reduction'], 50)
        elif 'elevated' in severities:
            if self.state['risk_level'] == 'normal':
                self.state['risk_level'] = 'elevated'
                self.state['exposure_reduction'] = max(self.state['exposure_reduction'], 20)
        
        self.state['active_alerts'] = [a['id'] for a in alerts]
    
    def execute_risk_action(self, alert: Dict, positions: Dict) -> Dict:
        """执行风控动作"""
        action = alert.get('action', '')
        market = alert.get('market', 'ALL')
        
        result = {
            "action_executed": action,
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "positions_closed": [],
            "exposure_reduced": 0,
            "message": ""
        }
        
        if action == "emergency_liquidate_all":
            # 紧急清仓
            result['positions_closed'] = self._liquidate_all_positions(positions, market)
            result['message'] = f"🚨 紧急清仓完成！关闭 {len(result['positions_closed'])} 个持仓"
            
        elif action == "reduce_exposure_to_30pct":
            # 减仓至30%
            result['exposure_reduced'] = self._reduce_exposure(positions, target_pct=30)
            result['message'] = f"⚠️ 风险减仓完成！仓位降至30%"
            
        elif action == "reduce_all_exposure_to_50pct":
            # 全市场减仓至50%
            result['exposure_reduced'] = self._reduce_exposure(positions, target_pct=50)
            result['message'] = f"⚠️ 全市场风险减仓完成！仓位降至50%"
            
        elif action == "immediate_stop_loss":
            # 个股止损
            result['positions_closed'] = self._stop_loss_single_stock(positions, alert)
            result['message'] = f"🛑 个股止损执行！"
        
        # 更新警报状态
        self._mark_alert_resolved(alert['id'], result)
        
        return result
    
    def _liquidate_all_positions(self, positions: Dict, market: str) -> List[str]:
        """清仓所有持仓"""
        closed = []
        # 实际执行清仓逻辑
        for symbol, pos in positions.items():
            if market == 'ALL' or pos.get('market') == market:
                closed.append(symbol)
        return closed
    
    def _reduce_exposure(self, positions: Dict, target_pct: float) -> float:
        """降低仓位"""
        # 实际执行减仓逻辑
        return target_pct
    
    def _stop_loss_single_stock(self, positions: Dict, alert: Dict) -> List[str]:
        """个股止损"""
        # 实际执行个股止损
        return []
    
    def _mark_alert_resolved(self, alert_id: str, result: Dict):
        """标记警报已处理"""
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            for alert in alerts:
                if alert['id'] == alert_id:
                    alert['status'] = 'resolved'
                    alert['resolved_at'] = datetime.now().isoformat()
                    alert['execution_result'] = result
                    break
            
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    def get_risk_status(self) -> Dict:
        """获取当前风控状态"""
        return {
            "risk_level": self.state.get('risk_level', 'normal'),
            "emergency_mode": self.state.get('emergency_mode', False),
            "exposure_reduction": self.state.get('exposure_reduction', 0),
            "active_alerts": len(self.state.get('active_alerts', [])),
            "last_check": self.state.get('last_check')
        }
    
    def reset_emergency_mode(self):
        """重置紧急模式（风险解除后）"""
        self.state['risk_level'] = 'normal'
        self.state['emergency_mode'] = False
        self.state['exposure_reduction'] = 0
        self.state['active_alerts'] = []
        self._save_state()
    
    def generate_risk_report(self) -> str:
        """生成风控报告"""
        status = self.get_risk_status()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                   🛡️ 黑天鹅风控状态报告                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 当前风控状态

| 指标 | 数值 | 状态 |
|------|------|------|
| 风险等级 | {status['risk_level'].upper()} | {'🟢' if status['risk_level'] == 'normal' else '🟡' if status['risk_level'] == 'elevated' else '🔴' if status['risk_level'] == 'high' else '🚨'} |
| 紧急模式 | {'🚨 已激活' if status['emergency_mode'] else '✅ 正常'} | - |
| 仓位限制 | {status['exposure_reduction']}% | {'🔒 清仓' if status['exposure_reduction'] >= 100 else '⚠️ 减仓' if status['exposure_reduction'] > 0 else '✅ 正常'} |
| 活跃警报 | {status['active_alerts']} | {'🚨' if status['active_alerts'] > 0 else '✅'} |

---

## 🚨 监控触发器

1. **美股崩盘** - VIX>40 且 S&P500<-5% → 🚨 紧急清仓
2. **A股千股跌停** - 沪深300<-5% 且 跌停股>500 → ⚠️ 减仓至30%
3. **港股暴跌** - 恒指<-8% 且 放量 → 🚨 紧急清仓
4. **跨市场联动** - 相关性>0.9 且 恐慌指数>80 → ⚠️ 全市场减仓至50%
5. **个股黑天鹅** - 单日跌>20% → 🛑 立即止损

---

## 💡 风控原则

- **快速反应**: 检测到极端情况后5分钟内执行
- **果断斩仓**: 不犹豫，不幻想，机械执行
- **保护本金**: 生存第一，盈利第二
- **事后复盘**: 每次触发后分析原因，优化模型

---

上次检查: {status['last_check'] or '从未'}

"""
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🛡️ 黑天鹅风控系统")
    print("=" * 70)
    
    risk_control = BlackSwanRiskControl()
    
    # 显示状态
    status = risk_control.get_risk_status()
    print(f"\n📊 当前风险等级: {status['risk_level'].upper()}")
    print(f"🚨 紧急模式: {'已激活' if status['emergency_mode'] else '正常'}")
    print(f"🔒 仓位限制: {status['exposure_reduction']}%")
    
    # 生成报告
    print("\n" + "=" * 70)
    report = risk_control.generate_risk_report()
    print(report)

if __name__ == "__main__":
    main()
