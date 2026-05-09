#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIO觉醒系统主控器
执行A+B双轨任务，整合所有结果
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, '/workspace/projects/workspace')

from A5L_v2.1_DEV.cio_awakening.cio_system import CIOAwakeningSystem
from A5L_v2.1_DEV.cio_awakening.task_a_validator import StrategyValidator
from A5L_v2.1_DEV.cio_awakening.task_b_trainer import MLModelTrainer

def main():
    """主执行函数"""
    print("=" * 70)
    print("🧠 CIO A股模拟交易觉醒系统 v1.0")
    print("🎯 A+B双轨任务执行")
    print("=" * 70)
    print()
    
    # 初始化系统
    cio = CIOAwakeningSystem()
    print(f"✅ 系统初始化完成: v{cio.version}")
    print(f"   数据源: {len(cio.data_sources)}个")
    print(f"   策略: {len(cio.strategies)}个")
    print(f"   ML模型: {len(cio.ml_models)}个")
    print()
    
    # 创建输出目录
    output_dir = Path('A5L_v2.1_DEV/cio_awakening/results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== A任务: 策略验证 ====================
    print("=" * 70)
    print("🎯 A任务: 现有策略8年历史验证")
    print("=" * 70)
    print()
    
    validator = StrategyValidator()
    a_results = validator.run_all_validations()
    
    # 保存A任务结果
    with open(output_dir / 'task_a_complete.json', 'w', encoding='utf-8') as f:
        json.dump(a_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ A任务完成! 结果保存至: {output_dir / 'task_a_complete.json'}")
    print()
    
    # ==================== B任务: ML训练 ====================
    print("=" * 70)
    print("🎯 B任务: CIO ML预测模型训练")
    print("=" * 70)
    print()
    
    trainer = MLModelTrainer()
    b_results = trainer.run_all_training()
    
    # 保存B任务结果
    with open(output_dir / 'task_b_complete.json', 'w', encoding='utf-8') as f:
        json.dump(b_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ B任务完成! 结果保存至: {output_dir / 'task_b_complete.json'}")
    print()
    
    # ==================== 整合报告 ====================
    print("=" * 70)
    print("📊 A+B双轨任务整合报告")
    print("=" * 70)
    print()
    
    final_report = {
        'system': 'CIO A股模拟交易觉醒系统',
        'version': '1.0.0',
        'execution_time': datetime.now().isoformat(),
        'task_a_validation': a_results,
        'task_b_training': b_results,
        'summary': {
            'strategies_validated': len(a_results.get('validations', [])),
            'models_trained': len(b_results.get('models', [])),
            'skills_integrated': [
                'yangguan-daodao (技术指标+浪主波浪)',
                'catalyst-tier-framework (CTF分级)',
                'factor-investing (多因子模型)',
                'kaipanla-api (8年历史数据)',
                'unified-backtest-engine (回测验证)',
                'track_validation_metrics (绩效跟踪)',
                'knowledge-graph (关联分析)'
            ],
            'next_steps': [
                '1. 获取真实8年K线数据重新验证',
                '2. 安装XGBoost/TensorFlow训练真实模型',
                '3. 集成到CIO模拟交易系统',
                '4. 启动09:15实时信号生成'
            ]
        }
    }
    
    # 保存最终报告
    with open(output_dir / 'cio_awakening_final_report.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False, default=str)
    
    print(json.dumps(final_report['summary'], indent=2, ensure_ascii=False))
    print()
    print("=" * 70)
    print(f"📁 所有结果保存至: {output_dir}")
    print("🎉 CIO觉醒系统任务完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
