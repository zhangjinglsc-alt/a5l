#!/usr/bin/env python3
"""
A5L 过程管理系统 v1.0 (Process Management System)
确保所有自动化任务过程有迹可循、可审计、可视化

核心能力:
1. 执行记录追踪
2. 学习过程记录
3. 监控事件记录
4. 异常处理记录
5. 审计链生成
6. 实时状态面板
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"

class Severity(Enum):
    P0 = "critical"  # 系统故障
    P1 = "high"      # 任务失败
    P2 = "medium"    # 性能下降
    P3 = "low"       # 警告

@dataclass
class ExecutionRecord:
    """执行记录数据结构"""
    execution_id: str
    timestamp_start: str
    timestamp_end: Optional[str] = None
    duration_ms: Optional[int] = None
    task_name: str = ""
    task_version: str = "1.0.0"
    status: str = "pending"
    inputs: Dict = None
    processing: Dict = None
    outputs: Dict = None
    metrics: Dict = None
    audit: Dict = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = {}
        if self.processing is None:
            self.processing = {}
        if self.outputs is None:
            self.outputs = {}
        if self.metrics is None:
            self.metrics = {}
        if self.audit is None:
            self.audit = {}
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def compute_hash(self) -> str:
        """计算记录哈希"""
        content = f"{self.execution_id}|{self.timestamp_start}|{self.task_name}|{self.status}"
        if self.outputs:
            content += f"|{json.dumps(self.outputs, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

@dataclass
class LearningRecord:
    """学习记录数据结构"""
    learning_id: str
    timestamp: str
    skill_id: str
    skill_version: str
    source_type: str  # feishu_doc, trading_record, market_data, cross_transfer
    source_id: str
    source_name: str
    source_hash: str
    knowledge_items: List[Dict]
    proficiency_before: float
    proficiency_after: float
    verification_status: str = "pending"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @property
    def proficiency_delta(self) -> float:
        return round(self.proficiency_after - self.proficiency_before, 4)

@dataclass
class MonitoringEvent:
    """监控事件数据结构"""
    event_id: str
    timestamp_detected: str
    event_type: str  # catalyst, anomaly, alert, opportunity
    severity: str
    source: str
    detector: str
    confidence: float
    raw_data_summary: str
    classification: Dict
    response_actions: List[str]
    notification_sent: bool
    requires_review: bool
    review_status: str = "pending"
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ExceptionRecord:
    """异常记录数据结构"""
    exception_id: str
    timestamp: str
    severity: str
    category: str
    task_name: str
    execution_id: Optional[str]
    error_message: str
    error_hash: str
    context: Dict
    response: Dict
    resolution: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ProcessManager:
    """过程管理核心类"""
    
    def __init__(self):
        self.workspace = "/workspace/projects/workspace"
        self.logs_dir = f"{self.workspace}/data/process_logs"
        self.reports_dir = f"{self.workspace}/data/process_reports"
        self.dashboard_dir = f"{self.workspace}/data/process_dashboard"
        
        # 当前日期
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.daily_log_dir = f"{self.logs_dir}/{self.current_date}"
        
        # 确保目录存在
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保目录结构存在"""
        dirs = [
            f"{self.logs_dir}/{self.current_date}",
            f"{self.reports_dir}/daily",
            f"{self.reports_dir}/weekly",
            f"{self.reports_dir}/monthly",
            self.dashboard_dir
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def _generate_id(self, prefix: str) -> str:
        """生成唯一ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{short_uuid}"
    
    def _get_current_time(self) -> str:
        """获取当前时间ISO格式"""
        return datetime.now().isoformat()
    
    def _compute_content_hash(self, content: Any) -> str:
        """计算内容哈希"""
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    # ============ 执行记录 ============
    
    def start_execution(self, task_name: str, task_version: str = "1.0.0",
                       inputs: Dict = None) -> ExecutionRecord:
        """开始记录一次执行"""
        execution_id = self._generate_id("exec")
        
        record = ExecutionRecord(
            execution_id=execution_id,
            timestamp_start=self._get_current_time(),
            task_name=task_name,
            task_version=task_version,
            status="running",
            inputs=inputs or {},
            audit={
                "executor": "system:cron",
                "session_id": self._generate_id("sess"),
                "ip_address": "127.0.0.1"
            }
        )
        
        return record
    
    def complete_execution(self, record: ExecutionRecord, status: str,
                          outputs: Dict = None, metrics: Dict = None,
                          processing: Dict = None) -> ExecutionRecord:
        """完成执行记录"""
        record.timestamp_end = self._get_current_time()
        record.status = status
        
        # 计算执行时长
        if record.timestamp_start:
            start = datetime.fromisoformat(record.timestamp_start)
            end = datetime.fromisoformat(record.timestamp_end)
            record.duration_ms = int((end - start).total_seconds() * 1000)
        
        if outputs:
            record.outputs = outputs
        if metrics:
            record.metrics = metrics
        if processing:
            record.processing = processing
        
        # 保存记录
        self._save_execution_record(record)
        
        # 更新审计链
        self._update_audit_chain(record)
        
        # 更新实时面板
        self._update_dashboard()
        
        return record
    
    def _save_execution_record(self, record: ExecutionRecord):
        """保存执行记录到文件"""
        log_file = f"{self.daily_log_dir}/execution.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    # ============ 学习记录 ============
    
    def record_learning(self, skill_id: str, skill_version: str,
                       source_type: str, source_id: str, source_name: str,
                       source_content: Any, knowledge_items: List[Dict],
                       proficiency_before: float, proficiency_after: float) -> LearningRecord:
        """记录学习过程"""
        
        learning_id = self._generate_id("learn")
        source_hash = self._compute_content_hash(source_content)
        
        record = LearningRecord(
            learning_id=learning_id,
            timestamp=self._get_current_time(),
            skill_id=skill_id,
            skill_version=skill_version,
            source_type=source_type,
            source_id=source_id,
            source_name=source_name,
            source_hash=source_hash,
            knowledge_items=knowledge_items,
            proficiency_before=proficiency_before,
            proficiency_after=proficiency_after,
            verification_status="verified"
        )
        
        # 保存记录
        self._save_learning_record(record)
        
        return record
    
    def _save_learning_record(self, record: LearningRecord):
        """保存学习记录到文件"""
        log_file = f"{self.daily_log_dir}/learning.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    # ============ 监控事件 ============
    
    def record_monitoring_event(self, event_type: str, severity: str,
                               source: str, detector: str, confidence: float,
                               raw_data: Any, classification: Dict,
                               response_actions: List[str],
                               notification_sent: bool = False) -> MonitoringEvent:
        """记录监控事件"""
        
        event_id = self._generate_id("evt")
        raw_data_summary = str(raw_data)[:200]  # 截断摘要
        
        record = MonitoringEvent(
            event_id=event_id,
            timestamp_detected=self._get_current_time(),
            event_type=event_type,
            severity=severity,
            source=source,
            detector=detector,
            confidence=confidence,
            raw_data_summary=raw_data_summary,
            classification=classification,
            response_actions=response_actions,
            notification_sent=notification_sent,
            requires_review=severity in ["critical", "high"]
        )
        
        # 保存记录
        self._save_monitoring_record(record)
        
        return record
    
    def _save_monitoring_record(self, record: MonitoringEvent):
        """保存监控记录到文件"""
        log_file = f"{self.daily_log_dir}/monitor.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    # ============ 异常记录 ============
    
    def record_exception(self, severity: str, category: str,
                        task_name: str, execution_id: Optional[str],
                        error_message: str, error_details: Any,
                        context: Dict = None) -> ExceptionRecord:
        """记录异常"""
        
        exception_id = self._generate_id("exc")
        error_hash = self._compute_content_hash(str(error_details))
        
        record = ExceptionRecord(
            exception_id=exception_id,
            timestamp=self._get_current_time(),
            severity=severity,
            category=category,
            task_name=task_name,
            execution_id=execution_id,
            error_message=error_message,
            error_hash=error_hash,
            context=context or {},
            response={
                "auto_retry": False,
                "retry_count": 0,
                "escalated": severity in ["P0", "P1"]
            }
        )
        
        # 保存记录
        self._save_exception_record(record)
        
        return record
    
    def _save_exception_record(self, record: ExceptionRecord):
        """保存异常记录到文件"""
        log_file = f"{self.daily_log_dir}/exception.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    # ============ 审计链 ============
    
    def _update_audit_chain(self, record: ExecutionRecord):
        """更新审计哈希链"""
        audit_file = f"{self.daily_log_dir}/audit_chain.json"
        
        # 计算当前记录哈希
        record_hash = record.compute_hash()
        timestamp = self._get_current_time()
        
        # 读取现有链
        chain = []
        if os.path.exists(audit_file):
            with open(audit_file, 'r', encoding='utf-8') as f:
                chain = json.load(f)
        
        # 获取前一个哈希
        prev_hash = chain[-1]["cumulative_hash"] if chain else "0" * 16
        
        # 计算累积哈希
        cumulative_hash = hashlib.sha256(
            f"{prev_hash}{record_hash}{timestamp}".encode()
        ).hexdigest()[:16]
        
        # 添加新链接
        chain.append({
            "timestamp": timestamp,
            "execution_id": record.execution_id,
            "record_hash": record_hash,
            "prev_hash": prev_hash,
            "cumulative_hash": cumulative_hash
        })
        
        # 保存
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(chain, f, indent=2, ensure_ascii=False)
    
    # ============ 可视化面板 ============
    
    def _update_dashboard(self):
        """更新实时面板数据"""
        # 获取今日统计
        stats = self._get_today_stats()
        
        dashboard_data = {
            "timestamp": self._get_current_time(),
            "today_stats": stats,
            "recent_executions": self._get_recent_executions(10),
            "system_health": self._calculate_health_score()
        }
        
        dashboard_file = f"{self.dashboard_dir}/current_status.json"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    def _get_today_stats(self) -> Dict:
        """获取今日执行统计"""
        log_file = f"{self.daily_log_dir}/execution.jsonl"
        
        if not os.path.exists(log_file):
            return {"total": 0, "success": 0, "failed": 0, "success_rate": 0}
        
        total = 0
        success = 0
        failed = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    total += 1
                    if record.get("status") == "success":
                        success += 1
                    elif record.get("status") == "failed":
                        failed += 1
        
        success_rate = round(success / total * 100, 1) if total > 0 else 0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success_rate
        }
    
    def _get_recent_executions(self, limit: int = 10) -> List[Dict]:
        """获取最近执行记录"""
        log_file = f"{self.daily_log_dir}/execution.jsonl"
        
        if not os.path.exists(log_file):
            return []
        
        records = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        # 返回最后N条
        return records[-limit:]
    
    def _calculate_health_score(self) -> Dict:
        """计算系统健康度"""
        stats = self._get_today_stats()
        
        # 基于成功率计算健康分
        success_score = stats["success_rate"]
        
        # 检查异常记录
        exc_file = f"{self.daily_log_dir}/exception.jsonl"
        exception_count = 0
        if os.path.exists(exc_file):
            with open(exc_file, 'r', encoding='utf-8') as f:
                exception_count = sum(1 for _ in f if _.strip())
        
        # 健康分 = 成功率 * 0.7 + (1 - 异常率) * 0.3
        exception_rate = min(exception_count / max(stats["total"], 1), 1)
        health_score = round(success_score * 0.7 + (1 - exception_rate) * 30, 1)
        
        return {
            "overall": health_score,
            "success_rate": success_score,
            "exception_count": exception_count,
            "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
        }
    
    # ============ 报告生成 ============
    
    def generate_daily_report(self) -> str:
        """生成日报"""
        stats = self._get_today_stats()
        health = self._calculate_health_score()
        
        report = {
            "date": self.current_date,
            "generated_at": self._get_current_time(),
            "executions": stats,
            "health": health,
            "learning_summary": self._get_learning_summary(),
            "monitoring_summary": self._get_monitoring_summary()
        }
        
        report_file = f"{self.reports_dir}/daily/{self.current_date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def _get_learning_summary(self) -> Dict:
        """获取学习汇总"""
        log_file = f"{self.daily_log_dir}/learning.jsonl"
        
        if not os.path.exists(log_file):
            return {"total_learnings": 0, "skills_affected": [], "total_proficiency_gain": 0}
        
        total = 0
        skills = set()
        total_gain = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    total += 1
                    skills.add(record.get("skill_id"))
                    total_gain += record.get("proficiency_after", 0) - record.get("proficiency_before", 0)
        
        return {
            "total_learnings": total,
            "skills_affected": list(skills),
            "total_proficiency_gain": round(total_gain, 4)
        }
    
    def _get_monitoring_summary(self) -> Dict:
        """获取监控汇总"""
        log_file = f"{self.daily_log_dir}/monitor.jsonl"
        
        if not os.path.exists(log_file):
            return {"total_events": 0, "by_severity": {}, "by_type": {}}
        
        total = 0
        by_severity = {}
        by_type = {}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    total += 1
                    sev = record.get("severity", "unknown")
                    typ = record.get("event_type", "unknown")
                    by_severity[sev] = by_severity.get(sev, 0) + 1
                    by_type[typ] = by_type.get(typ, 0) + 1
        
        return {
            "total_events": total,
            "by_severity": by_severity,
            "by_type": by_type
        }


# 全局过程管理器实例
_process_manager = None

def get_process_manager() -> ProcessManager:
    """获取过程管理器实例 (单例模式)"""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager


# ============ 便捷函数 ============

def log_execution_start(task_name: str, **kwargs) -> ExecutionRecord:
    """便捷函数：开始执行记录"""
    pm = get_process_manager()
    return pm.start_execution(task_name, **kwargs)

def log_execution_complete(record: ExecutionRecord, status: str, **kwargs) -> ExecutionRecord:
    """便捷函数：完成执行记录"""
    pm = get_process_manager()
    return pm.complete_execution(record, status, **kwargs)

def log_learning(skill_id: str, **kwargs) -> LearningRecord:
    """便捷函数：记录学习"""
    pm = get_process_manager()
    return pm.record_learning(skill_id, **kwargs)

def log_monitoring_event(**kwargs) -> MonitoringEvent:
    """便捷函数：记录监控事件"""
    pm = get_process_manager()
    return pm.record_monitoring_event(**kwargs)

def log_exception(**kwargs) -> ExceptionRecord:
    """便捷函数：记录异常"""
    pm = get_process_manager()
    return pm.record_exception(**kwargs)


if __name__ == "__main__":
    # 测试代码
    pm = get_process_manager()
    
    # 测试执行记录
    print("Testing execution logging...")
    exec_record = pm.start_execution("test_task", inputs={"param": "value"})
    import time
    time.sleep(0.1)
    pm.complete_execution(
        exec_record,
        status="success",
        outputs={"result": "ok"},
        metrics={"cpu": "10%"}
    )
    print(f"✅ Execution recorded: {exec_record.execution_id}")
    
    # 测试学习记录
    print("Testing learning logging...")
    learn_record = pm.record_learning(
        skill_id="test_skill",
        skill_version="1.0.0",
        source_type="feishu_doc",
        source_id="doc_123",
        source_name="Test Document",
        source_content="Test content for hashing",
        knowledge_items=[{"type": "concept", "content": "test"}],
        proficiency_before=0.5,
        proficiency_after=0.55
    )
    print(f"✅ Learning recorded: {learn_record.learning_id}")
    
    # 测试监控记录
    print("Testing monitoring logging...")
    event = pm.record_monitoring_event(
        event_type="catalyst",
        severity="high",
        source="news_feed",
        detector="catalyst_tier_framework",
        confidence=0.92,
        raw_data={"title": "Test news"},
        classification={"tier": "Tier_1", "sector": "AI"},
        response_actions=["notify"],
        notification_sent=True
    )
    print(f"✅ Event recorded: {event.event_id}")
    
    # 生成日报
    print("Generating daily report...")
    report_file = pm.generate_daily_report()
    print(f"✅ Report generated: {report_file}")
    
    # 查看面板
    dashboard_file = f"{pm.dashboard_dir}/current_status.json"
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r') as f:
            dashboard = json.load(f)
        print(f"\n📊 Dashboard Health Score: {dashboard['system_health']['overall']}")
    
    print("\n✅ All tests passed!")
