#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 数据一致性检查工具
定期检测飞书SignalArena与本地系统的数据一致性
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class DataConsistencyChecker:
    """数据一致性检查器"""
    
    def __init__(self):
        self.issues = []
        self.scores = {}
        
    def check_local_positions(self) -> Tuple[bool, Dict]:
        """检查本地持仓数据"""
        position_file = '/workspace/projects/workspace/data/positions/position_summary.json'
        
        if not os.path.exists(position_file):
            return False, {"error": "本地持仓文件不存在"}
        
        try:
            with open(position_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return True, {
                "positions_count": data.get("positions_count", 0),
                "total_value": data.get("total_value", 0),
                "cash": data.get("cash", 0),
                "last_sync": data.get("sync_time", "unknown")
            }
        except Exception as e:
            return False, {"error": str(e)}
    
    def check_simulation_status(self) -> Tuple[bool, Dict]:
        """检查模拟盘状态"""
        sim_file = '/workspace/projects/workspace/data/simulation/a_simulation_status.json'
        
        if not os.path.exists(sim_file):
            return False, {"error": "模拟盘状态文件不存在"}
        
        try:
            with open(sim_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return True, {
                "positions_count": data.get("positions_count", 0),
                "total_value": data.get("current_capital", 0),
                "cash": data.get("available_cash", 0),
                "last_update": data.get("last_update", "unknown")
            }
        except Exception as e:
            return False, {"error": str(e)}
    
    def check_signal_duplicates(self) -> Tuple[bool, List]:
        """检查信号重复"""
        signal_file = '/workspace/projects/workspace/data/architect_5l/signals/tracked_signals.json'
        
        if not os.path.exists(signal_file):
            return True, []  # 文件不存在视为无重复
        
        try:
            with open(signal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            signals = data.get("signals", [])
            signal_ids = [s.get("signal_id") for s in signals]
            duplicates = [sid for sid in set(signal_ids) if signal_ids.count(sid) > 1]
            
            return len(duplicates) == 0, duplicates
        except Exception as e:
            return False, [str(e)]
    
    def check_future_dates(self) -> Tuple[bool, List]:
        """检查未来日期记录"""
        # 检查本地文件中的日期
        issues = []
        today = datetime.now()
        
        files_to_check = [
            '/workspace/projects/workspace/data/positions/position_summary.json',
            '/workspace/projects/workspace/data/simulation/a_simulation_status.json'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查sync_time
                    sync_time = data.get("sync_time") or data.get("last_update")
                    if sync_time:
                        try:
                            sync_dt = datetime.fromisoformat(sync_time.replace('Z', '+00:00'))
                            if sync_dt > today:
                                issues.append(f"{file_path}: 未来同步时间 {sync_time}")
                        except:
                            pass
                except:
                    pass
        
        return len(issues) == 0, issues
    
    def run_full_check(self) -> Dict:
        """执行完整检查"""
        print("=" * 70)
        print("📊 A5L 数据一致性检查报告")
        print("=" * 70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 1. 本地持仓检查
        print("\n【检查1】本地持仓数据")
        print("-" * 70)
        ok, result = self.check_local_positions()
        if ok:
            print(f"✅ 持仓文件存在")
            print(f"   持仓数量: {result['positions_count']}")
            print(f"   总资产: ¥{result['total_value']:,.2f}")
            print(f"   现金: ¥{result['cash']:,.2f}")
            print(f"   最后同步: {result['last_sync']}")
            self.scores['local_positions'] = 100
        else:
            print(f"❌ 错误: {result.get('error')}")
            self.scores['local_positions'] = 0
            self.issues.append({"type": "local_positions", "message": result.get('error')})
        
        # 2. 模拟盘状态检查
        print("\n【检查2】模拟盘状态")
        print("-" * 70)
        ok, result = self.check_simulation_status()
        if ok:
            print(f"✅ 模拟盘状态正常")
            print(f"   持仓数量: {result['positions_count']}")
            print(f"   总资产: ¥{result['total_value']:,.2f}")
            print(f"   现金: ¥{result['cash']:,.2f}")
            print(f"   最后更新: {result['last_update']}")
            self.scores['simulation_status'] = 100
        else:
            print(f"❌ 错误: {result.get('error')}")
            self.scores['simulation_status'] = 0
            self.issues.append({"type": "simulation_status", "message": result.get('error')})
        
        # 3. 信号重复检查
        print("\n【检查3】信号重复性")
        print("-" * 70)
        ok, duplicates = self.check_signal_duplicates()
        if ok:
            print(f"✅ 无重复信号")
            self.scores['signal_uniqueness'] = 100
        else:
            print(f"⚠️  发现 {len(duplicates)} 组重复信号")
            for dup in duplicates[:3]:
                print(f"   - {dup}")
            self.scores['signal_uniqueness'] = max(0, 100 - len(duplicates) * 10)
            self.issues.append({"type": "signal_duplicates", "count": len(duplicates)})
        
        # 4. 未来日期检查
        print("\n【检查4】日期有效性")
        print("-" * 70)
        ok, future_issues = self.check_future_dates()
        if ok:
            print(f"✅ 无未来日期记录")
            self.scores['date_validity'] = 100
        else:
            print(f"⚠️  发现 {len(future_issues)} 条未来日期记录")
            for issue in future_issues[:3]:
                print(f"   - {issue}")
            self.scores['date_validity'] = max(0, 100 - len(future_issues) * 10)
            self.issues.append({"type": "future_dates", "count": len(future_issues)})
        
        # 5. 持仓一致性检查 (本地 vs 模拟盘)
        print("\n【检查5】持仓一致性")
        print("-" * 70)
        
        ok1, local = self.check_local_positions()
        ok2, sim = self.check_simulation_status()
        
        if ok1 and ok2:
            if local['positions_count'] == sim['positions_count']:
                print(f"✅ 持仓数量一致 ({local['positions_count']}只)")
                if abs(local['total_value'] - sim['total_value']) < 1:
                    print(f"✅ 总资产一致 (¥{local['total_value']:,.2f})")
                    self.scores['consistency'] = 100
                else:
                    diff = local['total_value'] - sim['total_value']
                    print(f"⚠️  总资产差异: ¥{diff:,.2f}")
                    self.scores['consistency'] = 80
                    self.issues.append({"type": "value_mismatch", "diff": diff})
            else:
                print(f"❌ 持仓数量不一致")
                print(f"   本地: {local['positions_count']}只")
                print(f"   模拟盘: {sim['positions_count']}只")
                self.scores['consistency'] = 20
                self.issues.append({"type": "position_count_mismatch"})
        else:
            print(f"❌ 无法比较 (数据缺失)")
            self.scores['consistency'] = 0
        
        # 综合评分
        print("\n" + "=" * 70)
        print("📈 综合评分")
        print("=" * 70)
        
        for category, score in self.scores.items():
            status = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            print(f"{status} {category:25s}: {score:3d}/100")
        
        overall_score = sum(self.scores.values()) / len(self.scores) if self.scores else 0
        
        print(f"\n{'🟢' if overall_score >= 80 else '🟡' if overall_score >= 60 else '🔴'} 综合评分: {overall_score:.1f}/100")
        
        # 问题汇总
        if self.issues:
            print(f"\n⚠️  发现问题: {len(self.issues)}项")
            for issue in self.issues:
                print(f"   • {issue['type']}: {issue.get('message', issue.get('count', ''))}")
        else:
            print(f"\n✅ 所有检查通过，无异常")
        
        print("=" * 70)
        
        return {
            "check_time": datetime.now().isoformat(),
            "overall_score": overall_score,
            "scores": self.scores,
            "issues": self.issues,
            "status": "healthy" if overall_score >= 80 else "warning" if overall_score >= 60 else "critical"
        }


def main():
    """主函数"""
    checker = DataConsistencyChecker()
    report = checker.run_full_check()
    
    # 保存报告
    os.makedirs('/workspace/projects/workspace/data/architect_5l/reports', exist_ok=True)
    report_file = f"/workspace/projects/workspace/data/architect_5l/reports/consistency_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 报告已保存: {report_file}")
    
    return report


if __name__ == "__main__":
    main()
