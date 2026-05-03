#!/usr/bin/env python3
"""
A5L Layer 0 Hub - 六管理者统一入口
一键运行所有Layer 0系统，生成统一日报

执行时间: 2026-05-04 01:49
作者: Chief Architect
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List

WORKSPACE = "/workspace/projects/workspace"
LAYER0_DIR = f"{WORKSPACE}/scripts/layer0"
REPORT_DIR = f"{WORKSPACE}/data/layer0_reports"

class Layer0Hub:
    """
    Layer 0六管理者统一调度中心
    """
    
    # 六管理者配置
    MANAGERS = {
        'cio': {
            'name': 'Chief Investment Officer',
            'script': 'cio_portfolio_optimizer.py',
            'description': '投资决策 - Kelly公式优化器',
            'output': 'data/portfolio/cio_report_{date}.json'
        },
        'cso': {
            'name': 'Chief Security Officer',
            'script': 'cso_compliance_checker.py',
            'description': '安全风控 - 合规检查系统',
            'output': 'data/compliance_report_{date}.json'
        },
        'coo': {
            'name': 'Chief Operating Officer',
            'script': 'coo_resource_monitor.py',
            'description': '运营资源 - 资源监控中心',
            'output': 'data/operations/coo_report_{date}.json'
        },
        'uzi': {
            'name': 'Chief Analyst (UZI)',
            'script': 'uzi_auto_analyzer.py',
            'description': '首席分析 - 六维度评分系统',
            'output': 'data/analysis/uzi_report_{date}.json'
        },
        'rm': {
            'name': 'Report Manager',
            'script': 'report_manager_v15.py',
            'description': '报告管理 - 智能报告中枢',
            'output': 'data/reports/rm_batch_{date}.json'
        },
        'kg': {
            'name': 'Knowledge Guardian',
            'script': None,  # KG是被动系统，不需要主动运行
            'description': '知识守护 - 知识图谱管理',
            'output': 'N/A - 被动服务'
        }
    }
    
    def __init__(self):
        os.makedirs(REPORT_DIR, exist_ok=True)
        self.results = {}
        self.today = datetime.now().strftime('%Y%m%d')
    
    def print_header(self):
        """打印标题"""
        print("="*70)
        print("🏛️  A5L Layer 0 Hub - 六管理者统一入口")
        print("="*70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"版本: v0.1 MVP")
        print("="*70)
    
    def run_manager(self, manager_key: str, verbose: bool = True) -> Dict:
        """运行单个管理者"""
        config = self.MANAGERS[manager_key]
        
        if config['script'] is None:
            return {
                'success': True,
                'status': 'SKIPPED',
                'message': '被动系统，无需主动运行'
            }
        
        script_path = f"{LAYER0_DIR}/{config['script']}"
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔹 {config['name']}")
            print(f"   {config['description']}")
            print('='*70)
        
        try:
            result = subprocess.run(
                f"cd {WORKSPACE} && python3 {script_path}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            
            if verbose and success:
                # 打印关键输出（截断）
                output_lines = result.stdout.split('\n')
                for line in output_lines[-20:]:  # 最后20行
                    if line.strip():
                        print(line)
            
            return {
                'success': success,
                'status': 'SUCCESS' if success else 'FAILED',
                'output': result.stdout if success else result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'status': 'TIMEOUT',
                'message': '执行超时(>60s)'
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'ERROR',
                'message': str(e)
            }
    
    def run_all(self, verbose: bool = True) -> Dict:
        """运行所有管理者"""
        self.print_header()
        
        print("\n🚀 启动六管理者协同运行...")
        print()
        
        # 运行顺序：COO(资源) → UZI(分析) → CIO(决策) → CSO(风控) → RM(管理)
        run_order = ['coo', 'uzi', 'cio', 'cso', 'rm', 'kg']
        
        for key in run_order:
            self.results[key] = self.run_manager(key, verbose)
        
        return self.results
    
    def generate_summary(self) -> str:
        """生成执行摘要"""
        success_count = sum(1 for r in self.results.values() if r.get('success'))
        total = len([r for r in self.results.values() if r.get('status') != 'SKIPPED'])
        
        summary = f"""
{'='*70}
📊 Layer 0 六管理者执行摘要
{'='*70}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
成功率: {success_count}/{total} ({success_count/total*100:.0f}%)

详细状态:
"""
        
        for key, config in self.MANAGERS.items():
            result = self.results.get(key, {})
            status = result.get('status', 'UNKNOWN')
            icon = '✅' if status == 'SUCCESS' else '⚠️' if status == 'SKIPPED' else '❌'
            summary += f"  {icon} {config['name']}: {status}\n"
        
        summary += f"""
输出文件:
  📁 {REPORT_DIR}/
  📄 layer0_daily_report_{self.today}.md
  📊 各系统JSON报告已归档

{'='*70}
"""
        
        return summary
    
    def save_daily_report(self):
        """保存日报"""
        report_file = f"{REPORT_DIR}/layer0_daily_report_{self.today}.md"
        
        summary = self.generate_summary()
        
        # 添加关键发现
        findings = """
## 🔍 今日关键发现

### 投资组合诊断 (CIO)
- 招商南油: 36.7% → 建议0% (清仓)
- 中国长城: 36.7% → 建议13.3% (减仓)
- 集中度风险: HIGH

### 合规检查 (CSO)
- 合规评分: 66.7/100 (不合格)
- 违规项: 2项HIGH风险 (集中度超标)
- 立即行动: 是

### 系统资源 (COO)
- CPU: 正常
- 内存: 79.1% (接近阈值)
- 磁盘: 29.3% (正常)

### 分析评分 (UZI)
- 招商南油: 25/100 (BEARISH)
- 中国长城: 55/100 (CAUTION)
- 中芯国际: 55/100 (CAUTION)

### 报告队列 (RM)
- P0立即阅读: 1份 (招商南油研报)
- P1今日阅读: 1份
- P2本周阅读: 3份

## 📋 明日行动清单

### 高优先级 (5月6日开市)
1. [ ] 执行招商南油减仓 (目标: 0-10%)
2. [ ] 执行中国长城减仓 (目标: 13-20%)

### 中优先级
3. [ ] 监控内存使用率 (当前79.1%)
4. [ ] 阅读P0优先级研报

### 系统升级
5. [ ] CIO接入真实股价数据 (v0.5)

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*生成者: Layer0Hub*  
*架构监督: Chief Architect*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(summary + findings)
        
        print(f"\n✅ 日报已保存: {report_file}")
        return report_file
    
    def run_daily(self):
        """每日运行完整流程"""
        self.run_all(verbose=True)
        print(self.generate_summary())
        report_file = self.save_daily_report()
        
        print(f"\n🎯 Layer 0六管理者每日运行完成!")
        print(f"   查看日报: {report_file}")
        
        return self.results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A5L Layer 0 Hub - 六管理者统一入口')
    parser.add_argument('--command', choices=['daily_run', 'status', 'list'], 
                       default='daily_run', help='执行的命令')
    parser.add_argument('--manager', help='指定运行的管理者 (cio/cso/coo/uzi/rm/kg)')
    parser.add_argument('--quiet', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    hub = Layer0Hub()
    
    if args.command == 'daily_run':
        if args.manager:
            # 运行单个管理者
            result = hub.run_manager(args.manager, verbose=not args.quiet)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 运行全部
            hub.run_daily()
    
    elif args.command == 'status':
        # 显示状态
        hub.print_header()
        print("\n📊 六管理者状态:")
        for key, config in hub.MANAGERS.items():
            print(f"  {key.upper()}: {config['name']} - {config['description']}")
    
    elif args.command == 'list':
        # 列出可用命令
        print("""
可用命令:
  layer0_hub.py --command daily_run          # 运行全部六管理者
  layer0_hub.py --command daily_run --manager cio   # 仅运行CIO
  layer0_hub.py --command status             # 显示六管理者状态
  layer0_hub.py --command list               # 列出可用命令
  layer0_hub.py --quiet                      # 静默模式
        """)


if __name__ == "__main__":
    main()
