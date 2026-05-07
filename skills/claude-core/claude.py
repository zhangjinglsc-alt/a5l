#!/usr/bin/env python3
"""
Claude - 核心智能体 v1.0.0
统一自我诊断、修复、进化的元控制层

用法:
    python3 claude.py check      # 完整检查周期
    python3 claude.py diagnose   # 仅诊断
    python3 claude.py heal       # 仅修复
    python3 claude.py evolve     # 生成进化提案
    python3 claude.py status     # 查看健康状态
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ClaudeCore:
    """Claude核心智能体 - 统一自我管理"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = Path(workspace)
        self.claude_dir = self.workspace / "skills/claude-core"
        self.memory_dir = self.workspace / "memory"
        
        # 确保目录存在
        self.claude_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 健康档案
        self.health_record_file = self.memory_dir / "claude_health_record.json"
        
        # 检测结果
        self.diagnosis = None
        self.health_score = 100
        self.issues = []
        self.fixes = []
        self.proposals = []
    
    # ═══════════════════════════════════════════════════════
    # Layer 2: 感知层 (Perception)
    # ═══════════════════════════════════════════════════════
    
    def perceive(self) -> Dict:
        """全面感知系统状态"""
        print("🔍 Claude 感知层扫描中...")
        print("=" * 60)
        
        scans = {
            "infrastructure": self._scan_infrastructure(),
            "skill_system": self._scan_skill_system(),
            "git_sync": self._scan_git_sync(),
            "knowledge_base": self._scan_knowledge_base(),
            "predictive": self._scan_predictive(),
        }
        
        # 计算健康分
        self.health_score = sum(s.get("score", 0) for s in scans.values()) // len(scans)
        
        # 收集问题
        self.issues = []
        for name, result in scans.items():
            if result.get("issues"):
                self.issues.extend([
                    {"source": name, **issue} for issue in result["issues"]
                ])
        
        print(f"\n📊 系统健康评分: {self.health_score}/100")
        print(f"⚠️  发现问题: {len(self.issues)} 个")
        
        return scans
    
    def _scan_infrastructure(self) -> Dict:
        """扫描基础设施"""
        print("  [1/5] 扫描基础设施...")
        
        issues = []
        critical_files = ["SOUL.md", "SKILL_REGISTRY.json"]
        
        for f in critical_files:
            if not (self.workspace / f).exists():
                issues.append({"type": "missing_file", "file": f, "severity": "high"})
        
        score = 100 - len(issues) * 30
        return {"score": max(0, score), "issues": issues}
    
    def _scan_skill_system(self) -> Dict:
        """扫描SKILL系统"""
        print("  [2/5] 扫描SKILL系统...")
        
        registry_file = self.workspace / "SKILL_REGISTRY.json"
        if not registry_file.exists():
            return {"score": 50, "issues": [{"type": "missing_registry", "severity": "high"}]}
        
        try:
            with open(registry_file) as f:
                data = json.load(f)
            total = data.get("summary", {}).get("total_skills", 0)
            score = min(100, int(total / 60 * 100))
            
            issues = []
            if total < 60:
                issues.append({"type": "low_skill_count", "current": total, "target": 60, "severity": "low"})
            
            return {"score": score, "issues": issues, "total_skills": total}
        except Exception as e:
            return {"score": 50, "issues": [{"type": "registry_error", "error": str(e), "severity": "medium"}]}
    
    def _scan_git_sync(self) -> Dict:
        """扫描Git同步状态"""
        print("  [3/5] 扫描Git同步...")
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            uncommitted = len([l for l in result.stdout.split('\n') if l.strip()])
            
            score = 100 - min(50, uncommitted * 2)
            issues = []
            
            if uncommitted > 10:
                issues.append({"type": "uncommitted_changes", "count": uncommitted, "severity": "medium"})
            
            return {"score": score, "issues": issues, "uncommitted": uncommitted}
        except Exception as e:
            return {"score": 70, "issues": [{"type": "git_error", "error": str(e), "severity": "low"}]}
    
    def _scan_knowledge_base(self) -> Dict:
        """扫描知识库"""
        print("  [4/5] 扫描知识库...")
        
        kg_ok = (self.workspace / "trading-review-wiki").exists()
        kw_ok = (self.workspace / "skills/karpathy-wiki/wiki/_index.md").exists()
        
        score = 100
        if not kg_ok: score -= 25
        if not kw_ok: score -= 25
        
        issues = []
        if not kg_ok:
            issues.append({"type": "kg_not_active", "severity": "low"})
        if not kw_ok:
            issues.append({"type": "kw_not_initialized", "severity": "low"})
        
        return {"score": score, "issues": issues, "kg": kg_ok, "kw": kw_ok}
    
    def _scan_predictive(self) -> Dict:
        """预测性扫描"""
        print("  [5/5] 预测性扫描...")
        
        predictions = []
        
        # 检查日志文件大小
        memory_dir = self.workspace / "memory"
        if memory_dir.exists():
            log_files = list(memory_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in log_files) / (1024*1024)
            if total_size > 100:
                predictions.append(f"内存日志较大({total_size:.1f}MB)，建议归档")
        
        return {"score": 90, "issues": [], "predictions": predictions}
    
    # ═══════════════════════════════════════════════════════
    # Layer 3: 认知层 (Cognition)
    # ═══════════════════════════════════════════════════════
    
    def cognize(self) -> Dict:
        """认知决策 - 分析问题并制定策略"""
        print("\n🧠 Claude 认知层决策中...")
        print("=" * 60)
        
        if not self.issues:
            print("✅ 系统健康，无需修复")
            return {"actions": [], "proposals": []}
        
        actions = []
        proposals = []
        
        for issue in self.issues:
            severity = issue.get("severity", "low")
            issue_type = issue.get("type")
            
            if severity == "high":
                # 严重问题 → 立即自动修复
                actions.append({"issue": issue, "action": "auto_fix", "priority": "P0"})
                print(f"  🔴 P0: {issue_type} → 立即自动修复")
                
            elif severity == "medium":
                # 中等问题 → 自动修复 + 通知
                actions.append({"issue": issue, "action": "auto_fix_notify", "priority": "P1"})
                print(f"  🟡 P1: {issue_type} → 自动修复并通知")
                
            elif severity == "low":
                # 轻微问题 → 记录或提案
                if issue_type in ["low_skill_count"]:
                    proposals.append({"issue": issue, "type": "evolution", "priority": "P2"})
                    print(f"  🟢 P2: {issue_type} → 生成进化提案")
                else:
                    print(f"  ⚪ P3: {issue_type} → 记录观察")
        
        return {"actions": actions, "proposals": proposals}
    
    # ═══════════════════════════════════════════════════════
    # Layer 1: 执行层 (Execution)
    # ═══════════════════════════════════════════════════════
    
    def execute(self, decisions: Dict) -> Dict:
        """执行修复和进化操作"""
        print("\n🔧 Claude 执行层行动中...")
        print("=" * 60)
        
        results = {
            "fixes": [],
            "notifications": [],
            "proposals_generated": []
        }
        
        # 执行修复
        for action in decisions.get("actions", []):
            result = self._execute_fix(action)
            results["fixes"].append(result)
        
        # 生成进化提案
        for proposal in decisions.get("proposals", []):
            generated = self._generate_evolution_proposal(proposal)
            results["proposals_generated"].append(generated)
        
        return results
    
    def _execute_fix(self, action: Dict) -> Dict:
        """执行单个修复"""
        issue = action.get("issue", {})
        issue_type = issue.get("type")
        
        print(f"  修复: {issue_type}...", end=" ")
        
        if issue_type == "missing_file":
            # 无法自动创建核心文件，需人工处理
            return {"status": "manual_required", "issue": issue_type, "message": "核心文件缺失需人工处理"}
        
        elif issue_type == "uncommitted_changes":
            # 自动Git提交
            try:
                subprocess.run(["git", "add", "-A"], cwd=self.workspace, capture_output=True)
                subprocess.run(
                    ["git", "commit", "-m", f"claude: auto-fix {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                    cwd=self.workspace,
                    capture_output=True
                )
                subprocess.run(["git", "push", "origin", "main"], cwd=self.workspace, capture_output=True)
                print("✅ Git提交并推送")
                return {"status": "success", "issue": issue_type, "action": "git_commit_push"}
            except Exception as e:
                print(f"❌ 失败: {e}")
                return {"status": "failed", "issue": issue_type, "error": str(e)}
        
        else:
            print("⚪ 跳过")
            return {"status": "skipped", "issue": issue_type}
    
    def _generate_evolution_proposal(self, proposal: Dict) -> Dict:
        """生成进化提案"""
        issue = proposal.get("issue", {})
        
        generated = {
            "id": f"EVO-{datetime.now().strftime('%Y%m%d')}-{len(self.proposals)+1:03d}",
            "title": f"扩展SKILL数量 (当前{issue.get('current', '?')})",
            "description": f"当前SKILL数量({issue.get('current', '?')})低于目标({issue.get('target', 60)})，建议创建新SKILL填补能力缺口",
            "priority": proposal.get("priority", "P2"),
            "created_at": datetime.now().isoformat()
        }
        
        self.proposals.append(generated)
        print(f"  生成提案: {generated['id']}")
        
        return generated
    
    # ═══════════════════════════════════════════════════════
    # 公共接口
    # ═══════════════════════════════════════════════════════
    
    def run_full_cycle(self) -> Dict:
        """运行完整周期: 感知→认知→执行"""
        print("\n" + "=" * 60)
        print("🤖 Claude 核心智能体启动")
        print("=" * 60)
        
        # 感知
        perception = self.perceive()
        
        # 认知
        cognition = self.cognize()
        
        # 执行
        execution = self.execute(cognition)
        
        # 归档
        self._save_health_record(perception, cognition, execution)
        
        # 简报
        self._print_summary(execution)
        
        return {
            "health_score": self.health_score,
            "issues_found": len(self.issues),
            "fixes_applied": len([f for f in execution.get("fixes", []) if f.get("status") == "success"]),
            "proposals": len(self.proposals),
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_health_record(self, perception, cognition, execution):
        """保存健康档案"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "health_score": self.health_score,
            "perception": {k: {"score": v.get("score")} for k, v in perception.items()},
            "issues": self.issues,
            "fixes": execution.get("fixes", []),
            "proposals": self.proposals
        }
        
        # 读取历史
        history = []
        if self.health_record_file.exists():
            try:
                with open(self.health_record_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        history.append(record)
        
        # 保留最近30条
        history = history[-30:]
        
        with open(self.health_record_file, 'w') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def _print_summary(self, execution):
        """打印简报"""
        print("\n" + "=" * 60)
        print("📋 Claude 执行简报")
        print("=" * 60)
        print(f"健康评分: {self.health_score}/100")
        print(f"发现问题: {len(self.issues)}")
        print(f"成功修复: {len([f for f in execution.get('fixes', []) if f.get('status') == 'success'])}")
        print(f"进化提案: {len(self.proposals)}")
        
        if self.proposals:
            print("\n📝 待处理进化提案:")
            for p in self.proposals:
                print(f"   • [{p['priority']}] {p['id']}: {p['title']}")
        
        print("=" * 60)
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        if self.health_record_file.exists():
            with open(self.health_record_file, 'r') as f:
                history = json.load(f)
            if history:
                return history[-1]
        
        return {"status": "no_record"}

def main():
    claude = ClaudeCore()
    
    if len(sys.argv) < 2:
        # 默认运行完整周期
        result = claude.run_full_cycle()
        return 0 if result["health_score"] >= 70 else 1
    
    command = sys.argv[1]
    
    if command == "check":
        result = claude.run_full_cycle()
        return 0 if result["health_score"] >= 70 else 1
    
    elif command == "diagnose":
        claude.perceive()
        return 0
    
    elif command == "heal":
        claude.perceive()
        cognition = claude.cognize()
        claude.execute(cognition)
        return 0
    
    elif command == "evolve":
        claude.perceive()
        cognition = claude.cognize()
        claude.execute(cognition)
        return 0
    
    elif command == "status":
        status = claude.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return 0
    
    else:
        print(f"未知命令: {command}")
        print("用法: python3 claude.py [check|diagnose|heal|evolve|status]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
