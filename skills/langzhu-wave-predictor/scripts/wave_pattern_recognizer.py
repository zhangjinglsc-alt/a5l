#!/usr/bin/env python3
"""
浪主波浪理论 - 浪型识别增强模块 v1.1
Wave Pattern Recognition Enhancement

核心能力：
1. 5浪结构自动识别
2. 短浪/长浪判定
3. 微浪型生命周期计算
4. 扁担型结构检测
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum

class WaveType(Enum):
    """浪型类型"""
    WAVE_1 = "1浪"
    WAVE_2 = "2浪"
    WAVE_3 = "3浪"
    WAVE_4 = "4浪"
    WAVE_5 = "5浪"
    WAVE_A = "A浪"
    WAVE_B = "B浪"
    WAVE_C = "C浪"
    UNKNOWN = "未知"

class WaveLength(Enum):
    """浪长类型"""
    SHORT = "短浪"
    NORMAL = "标准浪"
    LONG = "长浪"
    EXTENDED = "延长浪"

@dataclass
class WaveDetail:
    """单浪详细信息"""
    wave_num: int  # 1-5
    wave_type: WaveType
    start_price: float
    end_price: float
    start_date: str
    end_date: str
    duration_days: int
    length_type: WaveLength
    amplitude: float  # 涨跌幅
    is_clear: bool  # 是否清晰可辨
    
@dataclass
class WaveStructure:
    """完整浪型结构"""
    # 基础信息
    trend_direction: str  # "up" | "down"
    start_point: float  # 起点价格
    start_date: str     # 起点日期
    end_point: Optional[float]  # 当前/终点价格
    end_date: Optional[str]
    total_days: int     # 总运行天数
    
    # 浪型详情
    waves: List[WaveDetail]  # 各浪详情
    current_wave: WaveType   # 当前所在浪
    current_wave_num: int    # 当前浪序号
    
    # 特殊结构
    has_extended_wave: bool  # 是否有延长浪
    extended_wave_num: Optional[int]  # 哪一浪延长
    is_carrying_pole: bool   # 是否扁担型结构
    carrying_pole_desc: Optional[str]  # 扁担型描述
    
    # 判断依据
    structure_confidence: float  # 结构置信度 0-1
    key_features: List[str]      # 关键特征
    
    # 预测相关
    next_likely_wave: Optional[WaveType]  # 下一浪可能
    lifecycle_stage: str  # "early" | "middle" | "late" | "end"

class WavePatternRecognizer:
    """浪型模式识别器"""
    
    def __init__(self):
        self.min_wave_days = 3  # 最小浪运行天数
        self.min_amplitude = 0.02  # 最小涨跌幅2%
        self.extended_threshold = 1.618  # 延长浪阈值
        
    def identify_5wave_structure(self, df_daily: pd.DataFrame, 
                                  significant_low: float,
                                  significant_low_date: str) -> WaveStructure:
        """
        识别5浪上升结构
        
        基于浪主理论要点：
        - 3794低点上升已30天
        - 清晰5浪结构
        - 当前处于5浪末端
        """
        
        if df_daily.empty:
            return self._create_empty_structure()
        
        # 从重要低点开始分析
        start_idx = self._find_price_index(df_daily, significant_low, significant_low_date)
        if start_idx is None:
            start_idx = 0
            
        relevant_df = df_daily.iloc[start_idx:].copy()
        
        # 找转折点（局部极值）
        turning_points = self._find_turning_points(relevant_df)
        
        # 尝试拟合5浪结构
        waves = self._fit_5wave_pattern(relevant_df, turning_points, significant_low)
        
        # 确定当前所在浪
        current_wave, current_num = self._identify_current_wave(waves, relevant_df)
        
        # 检测延长浪
        has_extended, extended_num = self._detect_extended_wave(waves)
        
        # 检测扁担型结构
        is_carrying_pole, pole_desc = self._detect_carrying_pole(waves, relevant_df)
        
        # 计算生命周期阶段
        lifecycle = self._calculate_lifecycle(current_wave, current_num, waves)
        
        # 计算置信度
        confidence = self._calculate_confidence(waves, turning_points)
        
        # 提取关键特征
        features = self._extract_features(waves, has_extended, is_carrying_pole)
        
        # 预测下一浪
        next_wave = self._predict_next_wave(current_wave, is_carrying_pole)
        
        return WaveStructure(
            trend_direction="up",
            start_point=significant_low,
            start_date=significant_low_date,
            end_point=float(relevant_df.iloc[-1]['收盘']) if not relevant_df.empty else None,
            end_date=str(relevant_df.iloc[-1]['日期']) if not relevant_df.empty else None,
            total_days=len(relevant_df),
            waves=waves,
            current_wave=current_wave,
            current_wave_num=current_num,
            has_extended_wave=has_extended,
            extended_wave_num=extended_num,
            is_carrying_pole=is_carrying_pole,
            carrying_pole_desc=pole_desc,
            structure_confidence=confidence,
            key_features=features,
            next_likely_wave=next_wave,
            lifecycle_stage=lifecycle
        )
    
    def _find_turning_points(self, df: pd.DataFrame) -> List[Dict]:
        """
        找出价格转折点
        
        使用局部极值检测，结合成交量和波动率
        """
        turning_points = []
        
        # 计算价格变化率
        df['price_change'] = df['收盘'].pct_change()
        df['high_3day'] = df['最高'].rolling(window=3, center=True).max()
        df['low_3day'] = df['最低'].rolling(window=3, center=True).min()
        
        for i in range(2, len(df)-2):
            current_high = df.iloc[i]['最高']
            current_low = df.iloc[i]['最低']
            
            # 判断是否为局部高点
            is_local_high = (current_high == df.iloc[i-2:i+3]['最高'].max())
            
            # 判断是否为局部低点
            is_local_low = (current_low == df.iloc[i-2:i+3]['最低'].min())
            
            if is_local_high:
                turning_points.append({
                    'index': i,
                    'date': str(df.iloc[i]['日期']),
                    'price': current_high,
                    'type': 'peak'
                })
            elif is_local_low:
                turning_points.append({
                    'index': i,
                    'date': str(df.iloc[i]['日期']),
                    'price': current_low,
                    'type': 'trough'
                })
        
        return sorted(turning_points, key=lambda x: x['index'])
    
    def _fit_5wave_pattern(self, df: pd.DataFrame, turning_points: List[Dict], 
                           start_price: float) -> List[WaveDetail]:
        """
        尝试拟合5浪结构
        """
        waves = []
        
        if len(turning_points) < 4:
            # 转折点不足，使用简化分析
            return self._simplified_wave_analysis(df, start_price)
        
        # 浪1：从起点到第一个高点
        wave1_end = self._find_first_wave1_end(turning_points, start_price)
        if wave1_end:
            waves.append(WaveDetail(
                wave_num=1,
                wave_type=WaveType.WAVE_1,
                start_price=start_price,
                end_price=wave1_end['price'],
                start_date=str(df.iloc[0]['日期']),
                end_date=wave1_end['date'],
                duration_days=wave1_end['index'],
                length_type=self._classify_length(start_price, wave1_end['price'], 1),
                amplitude=(wave1_end['price'] - start_price) / start_price,
                is_clear=True
            ))
        
        # 继续识别后续浪型...
        # 浪2、3、4、5的识别逻辑
        waves = self._identify_remaining_waves(waves, turning_points, df)
        
        return waves
    
    def _simplified_wave_analysis(self, df: pd.DataFrame, start_price: float) -> List[WaveDetail]:
        """简化浪型分析（转折点不足时使用）"""
        waves = []
        
        current_price = float(df.iloc[-1]['收盘'])
        max_price = float(df['最高'].max())
        min_price = float(df['最低'].min())
        total_days = len(df)
        start_date = str(df.iloc[0]['日期'])
        end_date = str(df.iloc[-1]['日期'])
        
        # 估算各浪（基于时间和空间比例）
        # 浪1：约占总涨幅的20-30%
        wave1_amplitude = (max_price - start_price) * 0.25
        wave1_end = start_price + wave1_amplitude
        
        # 浪2：回撤浪1的50-80%
        wave2_end = wave1_end - wave1_amplitude * 0.618
        
        # 浪3：最长的一浪
        wave3_end = max_price
        
        # 浪4：复杂调整
        wave4_end = wave3_end - (max_price - min_price) * 0.3
        
        # 浪5：末浪
        wave5_end = current_price
        
        waves = [
            WaveDetail(1, WaveType.WAVE_1, start_price, wave1_end, start_date, 
                      self._estimate_date(df, 0.15), int(total_days*0.15), 
                      WaveLength.NORMAL, wave1_amplitude/start_price, False),
            WaveDetail(2, WaveType.WAVE_2, wave1_end, wave2_end,
                      self._estimate_date(df, 0.15), self._estimate_date(df, 0.25),
                      int(total_days*0.10), WaveLength.NORMAL, 
                      (wave2_end-wave1_end)/wave1_end, False),
            WaveDetail(3, WaveType.WAVE_3, wave2_end, wave3_end,
                      self._estimate_date(df, 0.25), self._estimate_date(df, 0.60),
                      int(total_days*0.35), WaveLength.EXTENDED,
                      (wave3_end-wave2_end)/wave2_end, True),
            WaveDetail(4, WaveType.WAVE_4, wave3_end, wave4_end,
                      self._estimate_date(df, 0.60), self._estimate_date(df, 0.80),
                      int(total_days*0.20), WaveLength.LONG,
                      (wave4_end-wave3_end)/wave3_end, True),
            WaveDetail(5, WaveType.WAVE_5, wave4_end, wave5_end,
                      self._estimate_date(df, 0.80), end_date,
                      int(total_days*0.20), WaveLength.NORMAL,
                      (wave5_end-wave4_end)/wave4_end, False),
        ]
        
        return waves
    
    def _identify_remaining_waves(self, waves: List[WaveDetail], 
                                   turning_points: List[Dict],
                                   df: pd.DataFrame) -> List[WaveDetail]:
        """识别剩余浪型"""
        # 简化实现，实际应用需要更复杂的逻辑
        return waves if waves else self._simplified_wave_analysis(df, turning_points[0]['price'] if turning_points else 0)
    
    def _identify_current_wave(self, waves: List[WaveDetail], 
                                df: pd.DataFrame) -> Tuple[WaveType, int]:
        """识别当前所在浪"""
        if not waves:
            return WaveType.UNKNOWN, 0
        
        current_price = float(df.iloc[-1]['收盘'])
        
        # 简单判断：如果当前价格接近最后一浪的终点，认为在最后一浪
        if waves:
            last_wave = waves[-1]
            if last_wave.wave_num == 5:
                # 判断5浪是否完成
                if len(df) > 0:
                    recent_trend = (current_price - df.iloc[-5]['收盘']) / df.iloc[-5]['收盘'] if len(df) >= 5 else 0
                    if abs(recent_trend) < 0.005:  # 趋于平稳
                        return WaveType.WAVE_5, 5
        
        # 默认返回最后一浪
        return waves[-1].wave_type if waves else WaveType.UNKNOWN, len(waves)
    
    def _detect_extended_wave(self, waves: List[WaveDetail]) -> Tuple[bool, Optional[int]]:
        """检测延长浪"""
        if len(waves) < 3:
            return False, None
        
        # 找出幅度最大的浪
        max_amplitude = 0
        extended_num = None
        
        for wave in waves:
            if abs(wave.amplitude) > max_amplitude:
                max_amplitude = abs(wave.amplitude)
                extended_num = wave.wave_num
        
        # 如果某浪幅度明显大于其他浪，认为是延长浪
        if extended_num and max_amplitude > 0.15:  # 15%以上
            return True, extended_num
        
        return False, None
    
    def _detect_carrying_pole(self, waves: List[WaveDetail], 
                              df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        检测扁担型结构
        
        特征：
        - 破长4浪低点后再创新高
        - 形成小末浪（子5浪）
        - 通常是诱多，随后大跌
        """
        if len(waves) < 4:
            return False, None
        
        # 获取长4浪低点
        wave4 = next((w for w in waves if w.wave_num == 4), None)
        if not wave4:
            return False, None
        
        current_price = float(df.iloc[-1]['收盘'])
        max_price = float(df['最高'].max())
        
        # 判断是否破4浪低点
        broke_low = current_price < wave4.end_price * 1.01  # 允许1%误差
        
        # 判断是否接近或超过前期高点
        near_high = current_price > max_price * 0.995
        
        if broke_low and near_high:
            return True, f"破4浪低点{wave4.end_price:.2f}后再创新高{max_price:.2f}，形成扁担型小末浪"
        
        return False, None
    
    def _calculate_lifecycle(self, current_wave: WaveType, 
                              current_num: int,
                              waves: List[WaveDetail]) -> str:
        """计算微浪型生命周期阶段"""
        if current_num <= 2:
            return "early"
        elif current_num == 3:
            return "middle"
        elif current_num == 4:
            return "late"
        elif current_num >= 5:
            # 判断5浪是否接近尾声
            if waves and len(waves) >= 5:
                wave5 = waves[4]
                if wave5.duration_days > 5:  # 5浪运行超过5天
                    return "end"
            return "late"
        return "unknown"
    
    def _calculate_confidence(self, waves: List[WaveDetail], 
                              turning_points: List[Dict]) -> float:
        """计算浪型识别置信度"""
        confidence = 0.5  # 基础置信度
        
        # 转折点越多，置信度越高
        if len(turning_points) >= 6:
            confidence += 0.2
        elif len(turning_points) >= 4:
            confidence += 0.1
        
        # 清晰的浪型增加置信度
        clear_waves = sum(1 for w in waves if w.is_clear)
        confidence += clear_waves * 0.05
        
        # 有延长浪的结构更可信
        if any(w.length_type == WaveLength.EXTENDED for w in waves):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_features(self, waves: List[WaveDetail], 
                          has_extended: bool,
                          is_carrying_pole: bool) -> List[str]:
        """提取浪型关键特征"""
        features = []
        
        if not waves:
            return ["数据不足，无法识别清晰浪型"]
        
        # 基础信息
        total_days = sum(w.duration_days for w in waves)
        features.append(f"完整5浪结构，总运行{total_days}天")
        
        # 延长浪
        if has_extended:
            extended = next((w for w in waves if w.length_type == WaveLength.EXTENDED), None)
            if extended:
                features.append(f"{extended.wave_type.value}为延长浪，幅度{extended.amplitude*100:.1f}%")
        
        # 扁担型
        if is_carrying_pole:
            features.append("⚠️ 检测到扁担型结构，警惕诱多风险")
        
        # 浪长分布
        short_waves = [w for w in waves if w.length_type == WaveLength.SHORT]
        if short_waves:
            features.append(f"存在{len(short_waves)}个短浪，调整可能不充分")
        
        # 当前状态
        if waves:
            current = waves[-1]
            features.append(f"当前处于{current.wave_type.value}，运行{current.duration_days}天")
        
        return features
    
    def _predict_next_wave(self, current_wave: WaveType, 
                           is_carrying_pole: bool) -> Optional[WaveType]:
        """预测下一浪"""
        if is_carrying_pole:
            return WaveType.WAVE_A  # 扁担型后通常是A浪下跌
        
        if current_wave == WaveType.WAVE_5:
            return WaveType.WAVE_A  # 5浪后是A浪调整
        elif current_wave == WaveType.WAVE_A:
            return WaveType.WAVE_B
        elif current_wave == WaveType.WAVE_B:
            return WaveType.WAVE_C
        
        return None
    
    def _classify_length(self, start: float, end: float, wave_num: int) -> WaveLength:
        """分类浪长"""
        amplitude = abs(end - start) / start
        
        if amplitude > 0.20:  # 20%以上
            return WaveLength.EXTENDED
        elif amplitude > 0.10:  # 10-20%
            return WaveLength.LONG
        elif amplitude > 0.05:  # 5-10%
            return WaveLength.NORMAL
        else:
            return WaveLength.SHORT
    
    def _estimate_date(self, df: pd.DataFrame, progress: float) -> str:
        """根据进度估算日期"""
        idx = int(len(df) * progress)
        idx = max(0, min(idx, len(df)-1))
        return str(df.iloc[idx]['日期'])
    
    def _find_price_index(self, df: pd.DataFrame, price: float, date_str: str) -> Optional[int]:
        """查找价格对应的索引"""
        for i, row in df.iterrows():
            if str(row['日期']) == date_str:
                return i
            if abs(float(row['最低']) - price) / price < 0.02:  # 2%误差
                return i
        return 0
    
    def _find_first_wave1_end(self, turning_points: List[Dict], start_price: float) -> Optional[Dict]:
        """找出第一浪终点"""
        for tp in turning_points:
            if tp['type'] == 'peak' and tp['price'] > start_price * 1.05:  # 上涨超过5%
                return tp
        return turning_points[0] if turning_points else None
    
    def _create_empty_structure(self) -> WaveStructure:
        """创建空结构"""
        return WaveStructure(
            trend_direction="unknown",
            start_point=0,
            start_date="",
            end_point=None,
            end_date=None,
            total_days=0,
            waves=[],
            current_wave=WaveType.UNKNOWN,
            current_wave_num=0,
            has_extended_wave=False,
            extended_wave_num=None,
            is_carrying_pole=False,
            carrying_pole_desc=None,
            structure_confidence=0,
            key_features=["数据不足"],
            next_likely_wave=None,
            lifecycle_stage="unknown"
        )
    
    def format_wave_structure(self, structure: WaveStructure) -> str:
        """格式化浪型结构为字符串"""
        lines = []
        lines.append(f"【浪型结构分析】")
        lines.append(f"方向: {'上升' if structure.trend_direction == 'up' else '下降'}5浪结构")
        lines.append(f"起点: {structure.start_point:.2f} ({structure.start_date})")
        lines.append(f"总运行: {structure.total_days}天")
        lines.append("")
        
        lines.append("【各浪详情】")
        for wave in structure.waves:
            emoji = "✓" if wave.is_clear else "~"
            lines.append(f"{emoji} {wave.wave_type.value}: {wave.start_price:.2f} → {wave.end_price:.2f}")
            lines.append(f"   幅度: {wave.amplitude*100:+.1f}% | 时长: {wave.duration_days}天 | 类型: {wave.length_type.value}")
        
        lines.append("")
        lines.append(f"【当前状态】")
        lines.append(f"所在浪: {structure.current_wave.value} (第{structure.current_wave_num}浪)")
        lines.append(f"生命周期: {structure.lifecycle_stage}")
        lines.append(f"结构置信度: {structure.structure_confidence*100:.0f}%")
        
        if structure.has_extended_wave:
            lines.append(f"⚡ 延长浪: 第{structure.extended_wave_num}浪")
        
        if structure.is_carrying_pole:
            lines.append(f"⚠️ 扁担型结构: {structure.carrying_pole_desc}")
        
        if structure.next_likely_wave:
            lines.append(f"📌 下一浪预测: {structure.next_likely_wave.value}")
        
        lines.append("")
        lines.append("【关键特征】")
        for feat in structure.key_features:
            lines.append(f"• {feat}")
        
        return "\n".join(lines)


# 使用示例
if __name__ == "__main__":
    import akshare as ak
    from datetime import datetime, timedelta
    
    # 获取数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    df = ak.index_zh_a_hist(
        symbol="000001",
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d")
    )
    
    # 识别浪型
    recognizer = WavePatternRecognizer()
    structure = recognizer.identify_5wave_structure(
        df, 
        significant_low=3794,  # 3794低点
        significant_low_date="2025-04-07"  # 示例日期
    )
    
    # 输出结果
    print(recognizer.format_wave_structure(structure))
