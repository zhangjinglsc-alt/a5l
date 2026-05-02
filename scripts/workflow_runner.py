#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Workflow Runner
执行技能融合和进化工作流
"""

import sys
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowRunner:
    def __init__(self, workflow_path: str):
        self.workflow_path = Path(workflow_path)
        self.workflow = None
        self.results = []
        
    def load_workflow(self):
        """加载工作流定义"""
        try:
            with open(self.workflow_path, 'r') as f:
                self.workflow = yaml.safe_load(f)
            logger.info(f"工作流加载成功: {self.workflow_path}")
            return True
        except Exception as e:
            logger.error(f"工作流加载失败: {e}")
            return False
    
    def execute_step(self, step: dict):
        """执行单个步骤"""
        step_name = step.get('name', 'unnamed')
        step_type = step.get('type', 'shell')
        
        logger.info(f"执行步骤: {step_name}")
        
        if step_type == 'shell':
            import subprocess
            cmd = step.get('command', '')
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=step.get('timeout', 300)
                )
                return {
                    'step': step_name,
                    'status': 'success' if result.returncode == 0 else 'failed',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            except Exception as e:
                return {
                    'step': step_name,
                    'status': 'error',
                    'error': str(e)
                }
        
        elif step_type == 'python':
            code = step.get('code', '')
            try:
                exec_globals = {}
                exec(code, exec_globals)
                return {
                    'step': step_name,
                    'status': 'success',
                    'output': exec_globals.get('result', None)
                }
            except Exception as e:
                return {
                    'step': step_name,
                    'status': 'error',
                    'error': str(e)
                }
        
        return {'step': step_name, 'status': 'skipped'}
    
    def run(self):
        """运行工作流"""
        if not self.load_workflow():
            return {'status': 'failed', 'error': '无法加载工作流'}
        
        name = self.workflow.get('name', 'unnamed')
        version = self.workflow.get('version', '1.0')
        steps = self.workflow.get('steps', [])
        
        logger.info(f"开始执行工作流: {name} (v{version})")
        logger.info(f"总步骤数: {len(steps)}")
        
        results = []
        for step in steps:
            result = self.execute_step(step)
            results.append(result)
            
            if result['status'] != 'success' and not step.get('continue_on_error', False):
                logger.error(f"步骤失败，终止工作流: {result.get('error', 'unknown error')}")
                break
        
        return {
            'workflow': name,
            'version': version,
            'status': 'completed',
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python workflow_runner.py <workflow.yaml>")
        sys.exit(1)
    
    workflow_path = sys.argv[1]
    runner = WorkflowRunner(workflow_path)
    result = runner.run()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 返回状态码
    if result.get('status') == 'completed':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
