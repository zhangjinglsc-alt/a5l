#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime, timedelta
import subprocess
import sys

BASE_DIR = "/workspace/projects/workspace/.circuit_breaker"
STATE_DIR = os.path.join(BASE_DIR, "state")
LOG_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_PATH = os.path.join(BASE_DIR, "config/default.json")

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_task_rules(task_name):
    config = load_config()
    default = config["default_rules"]
    overrides = config["task_overrides"].get(task_name, {})
    return {**default, **overrides}

def get_task_state_path(task_name):
    return os.path.join(STATE_DIR, f"{task_name}.json")

def load_task_state(task_name):
    path = get_task_state_path(task_name)
    if not os.path.exists(path):
        return {
            "task_name": task_name,
            "status": "normal",
            "failure_count": 0,
            "last_failure_time": None,
            "fuse_triggered_time": None,
            "failures": []
        }
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_task_state(task_name, state):
    path = get_task_state_path(task_name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def log_event(task_name, event_type, message):
    log_file = os.path.join(LOG_DIR, f"circuit_breaker_{datetime.now().strftime('%Y%m%d')}.log")
    log_line = f"[{datetime.now().isoformat()}] [{task_name}] [{event_type}] {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line)
    print(log_line.strip())

def send_notification(task_name, message):
    rules = get_task_rules(task_name)
    if not rules["notify_on_trigger"]:
        return
    # 发送飞书通知
    try:
        notify_msg = f"⚠️ 任务熔断通知\n任务: {task_name}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n详情: {message}"
        subprocess.run([
            "/usr/bin/node", "/usr/lib/node_modules/openclaw/bin/openclaw.js",
            "message", "send", "--to", "user:ou_15b3ad56ed656d75824368e8398e330b",
            "--message", notify_msg
        ], check=True, capture_output=True)
    except Exception as e:
        log_event(task_name, "NOTIFY_FAILED", f"发送通知失败: {str(e)}")

def check_fuse(task_name):
    """检查任务是否被熔断，返回True表示被熔断，不能执行"""
    state = load_task_state(task_name)
    rules = get_task_rules(task_name)
    
    if state["status"] == "fused":
        # 检查是否过了冷却时间
        fuse_time = datetime.fromisoformat(state["fuse_triggered_time"])
        if datetime.now() - fuse_time < timedelta(minutes=rules["cool_down_minutes"]):
            return True
        else:
            # 自动恢复
            state["status"] = "normal"
            state["failure_count"] = 0
            state["failures"] = []
            save_task_state(task_name, state)
            log_event(task_name, "AUTO_RECOVER", "熔断冷却时间已过，自动恢复任务执行")
            send_notification(task_name, "任务已自动恢复执行")
            return False
    return False

def record_success(task_name):
    """记录任务执行成功"""
    state = load_task_state(task_name)
    state["failure_count"] = 0
    state["failures"] = []
    if state["status"] == "fused":
        state["status"] = "normal"
        log_event(task_name, "RECOVERED", "任务执行成功，已从熔断状态恢复")
        send_notification(task_name, "任务执行成功，已恢复正常")
    save_task_state(task_name, state)
    log_event(task_name, "SUCCESS", "任务执行成功")

def record_failure(task_name, error_msg=""):
    """记录任务执行失败，判断是否触发熔断"""
    state = load_task_state(task_name)
    rules = get_task_rules(task_name)
    
    now = datetime.now()
    state["failures"].append({
        "time": now.isoformat(),
        "error": error_msg
    })
    # 清理超出时间窗口的失败记录
    time_window = timedelta(minutes=rules["time_window_minutes"])
    state["failures"] = [
        f for f in state["failures"]
        if now - datetime.fromisoformat(f["time"]) < time_window
    ]
    state["failure_count"] = len(state["failures"])
    state["last_failure_time"] = now.isoformat()
    
    if state["failure_count"] >= rules["failure_threshold"] and state["status"] != "fused":
        # 触发熔断
        state["status"] = "fused"
        state["fuse_triggered_time"] = now.isoformat()
        msg = f"任务连续失败{state['failure_count']}次，已触发熔断，冷却时间{rules['cool_down_minutes']}分钟"
        log_event(task_name, "FUSE_TRIGGERED", msg)
        send_notification(task_name, msg)
    
    save_task_state(task_name, state)
    log_event(task_name, "FAILURE", f"执行失败: {error_msg} (当前失败次数: {state['failure_count']})")

def get_fused_tasks():
    """获取当前所有被熔断的任务"""
    fused = []
    for filename in os.listdir(STATE_DIR):
        if not filename.endswith(".json"):
            continue
        task_name = filename[:-5]
        if check_fuse(task_name):
            fused.append(task_name)
    return fused

def manual_recover(task_name):
    """手动恢复熔断的任务"""
    state = load_task_state(task_name)
    if state["status"] != "fused":
        print(f"任务 {task_name} 未处于熔断状态")
        return
    state["status"] = "normal"
    state["failure_count"] = 0
    state["failures"] = []
    save_task_state(task_name, state)
    log_event(task_name, "MANUAL_RECOVER", "手动恢复任务执行")
    send_notification(task_name, "任务已被手动恢复执行")
    print(f"任务 {task_name} 已恢复")

def show_status():
    """显示所有任务的熔断状态"""
    print("=== 任务熔断状态 ===")
    for filename in sorted(os.listdir(STATE_DIR)):
        if not filename.endswith(".json"):
            continue
        task_name = filename[:-5]
        state = load_task_state(task_name)
        is_fused = check_fuse(task_name)
        status = "🔴 熔断中" if is_fused else "🟢 正常"
        print(f"{task_name:<40} {status} 失败次数: {state['failure_count']}")
        if is_fused:
            fuse_time = datetime.fromisoformat(state["fuse_triggered_time"])
            rules = get_task_rules(task_name)
            recover_time = fuse_time + timedelta(minutes=rules["cool_down_minutes"])
            print(f"  熔断时间: {fuse_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  预计恢复: {recover_time.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  task_circuit_breaker.py status                          # 查看所有任务状态")
        print("  task_circuit_breaker.py check <task_name>               # 检查任务是否被熔断")
        print("  task_circuit_breaker.py record_success <task_name>      # 记录成功")
        print("  task_circuit_breaker.py record_failure <task_name> [msg]# 记录失败")
        print("  task_circuit_breaker.py recover <task_name>             # 手动恢复任务")
        print("  task_circuit_breaker.py fused                           # 列出所有熔断的任务")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "status":
        show_status()
    elif action == "check":
        if len(sys.argv) < 3:
            print("请指定任务名")
            sys.exit(1)
        task_name = sys.argv[2]
        is_fused = check_fuse(task_name)
        sys.exit(1 if is_fused else 0)
    elif action == "record_success":
        if len(sys.argv) < 3:
            print("请指定任务名")
            sys.exit(1)
        record_success(sys.argv[2])
    elif action == "record_failure":
        if len(sys.argv) < 3:
            print("请指定任务名")
            sys.exit(1)
        task_name = sys.argv[2]
        error_msg = sys.argv[3] if len(sys.argv) > 3 else ""
        record_failure(task_name, error_msg)
    elif action == "recover":
        if len(sys.argv) < 3:
            print("请指定任务名")
            sys.exit(1)
        manual_recover(sys.argv[2])
    elif action == "fused":
        fused = get_fused_tasks()
        if fused:
            print("当前熔断的任务:")
            for t in fused:
                print(f"  - {t}")
        else:
            print("无熔断的任务")
    else:
        print(f"未知操作: {action}")
        sys.exit(1)
