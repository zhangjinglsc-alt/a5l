"""
《改造我们的学习》 - 学习型组织与复盘进化系统
对应毛选：实事求是、反对主观主义、持续学习
"""

from typing import Dict, List
from datetime import datetime


class LearningOrganizationSystem:
    """
    学习型组织与复盘进化系统
    
    核心思想：
    - 每日复盘：记录交易、分析对错
    - 每周总结：提炼模式、改进策略
    - 每月进化：更新框架、迭代系统
    """
    
    def __init__(self):
        self.learning_coefficient = 0.1
        self.recovery_coefficient = 0.05
        self.review_history = []
        self.patterns = {}
    
    def conduct_daily_review(self, trading_day: dict) -> dict:
        """每日复盘"""
        date = trading_day['date']
        trades = trading_day.get('trades', [])
        
        review = {
            'date': date,
            'trades_analysis': [],
            'lessons_learned': []
        }
        
        for trade in trades:
            analysis = self._analyze_trade(trade)
            review['trades_analysis'].append(analysis)
            
            if analysis['was_profitable']:
                review['lessons_learned'].append({
                    'type': 'success',
                    'lesson': analysis.get('success_factor', '')
                })
            else:
                review['lessons_learned'].append({
                    'type': 'failure',
                    'lesson': analysis.get('improvement_suggestion', '')
                })
        
        self.review_history.append(review)
        return review
    
    def evaluate_learning_progress(self) -> dict:
        """评估学习进化进度"""
        if len(self.review_history) < 10:
            return {'status': 'insufficient_data'}
        
        early = self.review_history[:10]
        recent = self.review_history[-10:]
        
        early_wins = sum([1 for r in early for t in r.get('trades_analysis', []) if t.get('was_profitable', False)])
        recent_wins = sum([1 for r in recent for t in r.get('trades_analysis', []) if t.get('was_profitable', False)])
        
        early_rate = early_wins / max(1, sum([len(r.get('trades_analysis', [])) for r in early]))
        recent_rate = recent_wins / max(1, sum([len(r.get('trades_analysis', [])) for r in recent]))
        
        effect = recent_rate - early_rate
        
        return {
            'early_win_rate': early_rate,
            'recent_win_rate': recent_rate,
            'learning_effect': effect,
            'status': 'improving' if effect > 0 else 'stagnant'
        }
    
    def _analyze_trade(self, trade: dict) -> dict:
        """分析单笔交易"""
        pnl = trade.get('pnl', 0)
        return {
            'trade': trade,
            'pnl': pnl,
            'was_profitable': pnl > 0,
            'success_factor': self._identify_success_factor(trade) if pnl > 0 else None,
            'improvement_suggestion': self._suggest_improvement(trade) if pnl <= 0 else None
        }
    
    def _identify_success_factor(self, trade: dict) -> str:
        """识别成功因素"""
        return '时机把握准确' if trade.get('good_timing', False) else '综合因素'
    
    def _suggest_improvement(self, trade: dict) -> str:
        """提出改进建议"""
        if not trade.get('had_stop_loss', False):
            return '所有交易必须预设止损点'
        return '复盘具体原因'
