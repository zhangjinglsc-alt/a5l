#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L3 P0: 分析推理链系统
提出者: Chief Architect (顶级架构师)
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    step_id: str
    description: str
    input_data: Dict
    reasoning_process: str
    output_conclusion: str
    confidence: float
    evidence: List[str] = field(default_factory=list)

class ReasoningChain:
    """分析推理链 - P0最高优先级"""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        self.steps = []
        self.final_conclusion = ""
        self.overall_confidence = 0.0
        logger.info(f"🧠 Reasoning Chain initialized: {analysis_id}")
    
    def add_step(self, description: str, input_data: Dict,
                reasoning: str, conclusion: str, 
                confidence: float, evidence: List[str] = None) -> ReasoningStep:
        """添加推理步骤"""
        step = ReasoningStep(
            step_id=f"step_{len(self.steps) + 1}",
            description=description,
            input_data=input_data,
            reasoning_process=reasoning,
            output_conclusion=conclusion,
            confidence=confidence,
            evidence=evidence or []
        )
        
        self.steps.append(step)
        logger.info(f"➕ Added reasoning step: {description}")
        return step
    
    def finalize(self, final_conclusion: str):
        """完成推理链"""
        self.final_conclusion = final_conclusion
        self.overall_confidence = np.mean([s.confidence for s in self.steps]) if self.steps else 0
        
        logger.info(f"✅ Reasoning chain finalized: {final_conclusion}")
    
    def export_chain(self) -> Dict:
        """导出完整推理链"""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': datetime.now().isoformat(),
            'steps': [
                {
                    'step_id': s.step_id,
                    'description': s.description,
                    'reasoning': s.reasoning_process,
                    'conclusion': s.output_conclusion,
                    'confidence': s.confidence,
                    'evidence': s.evidence
                }
                for s in self.steps
            ],
            'final_conclusion': self.final_conclusion,
            'overall_confidence': self.overall_confidence
        }
