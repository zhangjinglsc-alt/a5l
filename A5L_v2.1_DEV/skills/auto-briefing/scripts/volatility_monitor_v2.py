#!/usr/bin/env python3
"""
智能分层波动监控系统 v2.0
监控A股主要指数波动，动态调整检查频率

规则：
- 交易时间 9:15-15:00 运行
- 波动<5%：每15分钟检查
- 波动≥5%：每5分钟检查  
- 波动≥10%：每1分钟检查
- 降波后自动降低频次
"""

import json
import time
import logging
import akshare as ak
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional

# 配置
STATE_FILE = Path("/workspace/projects/workspace/skills/auto-briefing/data/volatility_state.json")
LOG_FILE = Path("/workspace/projects/workspace/skills/auto-briefing/data/volatility_monitor.log")
DATA_DIR = Path("/workspace/projects/workspace/skills/auto-briefing/data")

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 监控配置
THRESHOLDS = {
    'normal': 0.05,      # 5%
    'high': 0.10,        # 10%
}

CHECK_INTERVALS = {
    'calm': 900,         # 15分钟 (正常)
    'elevated': 300,     # 5分钟 (≥5%)
    'extreme': 60,       # 1分钟 (≥10%)
}

INDEX_CODES = {
    '上证指数': 'sh000001',
    '深证成指': 'sz399001',
    '创业板指': 'sz399006',
    '科创50': 'sh000688',
}

class VolatilityMonitor:
    def __init__(self):
        self.state = self.load_state()
        self.current_level = 'calm'
        self.last_prices: Dict[str, float] = {}
        
    def load_state(self) -> dict:
        """加载状态文件"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态失败: {e}")
        return {
            'last_check': None,
            'max_volatility': 0.0,
            'alert_count': 0,
            'check_count': 0,
            'start_time': datetime.now().isoformat(),
        }
    
    def save_state(self):
        """保存状态文件"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def is_trading_time(self) -> bool:
        """检查是否在交易时间"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周末不交易
        if weekday >= 5:
            return False
        
        # 检查是否在 9:15-15:00
        start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        end_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        
        return start_time <= now < end_time
    
    def get_index_data(self) -> Dict[str, dict]:
        """获取指数实时数据"""
        data = {}
        try:
            # 使用 akshare 获取实时行情
            df = ak.stock_zh_index_spot_em()
            
            for name, code in INDEX_CODES.items():
                row = df[df['代码'] == code.replace('sh', '').replace('sz', '')]
                if not row.empty:
                    data[name] = {
                        'code': code,
                        'price': float(row['最新价'].values[0]),
                        'change_pct': float(row['涨跌幅'].values[0]) / 100,
                        'change': float(row['涨跌额'].values[0]),
                        'volume': float(row['成交量'].values[0]),
                    }
        except Exception as e:
            logger.error(f"获取指数数据失败: {e}")
        
        return data
    
    def calculate_volatility(self, data: Dict[str, dict]) -> Tuple[float, str]:
        """计算整体波动率，返回(最大波动, 触发指数)"""
        max_vol = 0.0
        max_index = ""
        
        for name, info in data.items():
            vol = abs(info['change_pct'])
            if vol > max_vol:
                max_vol = vol
                max_index = name
        
        return max_vol, max_index
    
    def determine_check_interval(self, volatility: float) -> int:
        """根据波动率确定检查间隔（秒）"""
        if volatility >= THRESHOLDS['high']:
            return CHECK_INTERVALS['extreme']
        elif volatility >= THRESHOLDS['normal']:
            return CHECK_INTERVALS['elevated']
        else:
            return CHECK_INTERVALS['calm']
    
    def get_level_name(self, interval: int) -> str:
        """获取级别名称"""
        if interval == CHECK_INTERVALS['extreme']:
            return 'extreme'
        elif interval == CHECK_INTERVALS['elevated']:
            return 'elevated'
        return 'calm'
    
    def send_alert(self, data: Dict[str, dict], volatility: float, trigger: str):
        """发送波动警报"""
        level_emoji = "🔴" if volatility >= 0.10 else "🟠" if volatility >= 0.05 else "🟢"
        level_text = "剧烈波动" if volatility >= 0.10 else "显著波动" if volatility >= 0.05 else "正常波动"
        
        lines = [
            f"{level_emoji} 市场波动警报 ({datetime.now().strftime('%H:%M:%S')})",
            f"",
            f"【波动级别】{level_text} ({volatility*100:.2f}%)",
            f"【触发指数】{trigger}",
            f"",
            "【指数行情】",
        ]
        
        for name, info in data.items():
            emoji = "🔺" if info['change_pct'] > 0 else "🔻" if info['change_pct'] < 0 else "➖"
            lines.append(f"{emoji} {name}: {info['price']:.2f} ({info['change_pct']*100:+.2f}%)")
        
        lines.append(f"")
        lines.append(f"【当前监控频率】每{self.determine_check_interval(volatility)//60}分钟")
        
        alert_msg = "\n".join(lines)
        logger.info(f"\n{alert_msg}")
        
        # 保存警报到文件
        alert_file = DATA_DIR / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(alert_file, 'w') as f:
                f.write(alert_msg)
        except Exception as e:
            logger.error(f"保存警报失败: {e}")
    
    def run_check(self) -> int:
        """执行一次检查，返回下次检查间隔（秒）"""
        self.state['check_count'] += 1
        
        # 获取数据
        data = self.get_index_data()
        if not data:
            logger.warning("未获取到指数数据")
            return CHECK_INTERVALS['calm']
        
        # 计算波动率
        volatility, trigger = self.calculate_volatility(data)
        
        # 更新最大波动记录
        if volatility > self.state['max_volatility']:
            self.state['max_volatility'] = volatility
        
        # 确定检查间隔
        interval = self.determine_check_interval(volatility)
        new_level = self.get_level_name(interval)
        
        # 级别变化或显著波动时发送警报
        if new_level != self.current_level or volatility >= THRESHOLDS['normal']:
            if new_level != self.current_level:
                logger.info(f"监控级别变化: {self.current_level} -> {new_level}")
                self.current_level = new_level
            
            self.send_alert(data, volatility, trigger)
            self.state['alert_count'] += 1
        else:
            # 正常波动，只记录日志
            logger.info(f"正常监控 | 最大波动: {volatility*100:.2f}% ({trigger}) | 下次检查: {interval//60}分钟后")
        
        # 保存当前价格用于下次比较
        for name, info in data.items():
            self.last_prices[name] = info['price']
        
        self.state['last_check'] = datetime.now().isoformat()
        self.save_state()
        
        return interval
    
    def run(self):
        """主运行循环"""
        logger.info("=" * 50)
        logger.info("智能分层波动监控系统启动")
        logger.info("=" * 50)
        logger.info(f"交易时间: 9:15-15:00")
        logger.info(f"监控指数: {', '.join(INDEX_CODES.keys())}")
        logger.info(f"阈值配置: 正常<5% | 显著≥5% | 剧烈≥10%")
        logger.info("=" * 50)
        
        while True:
            try:
                # 检查是否在交易时间
                if not self.is_trading_time():
                    now = datetime.now()
                    if now.weekday() >= 5:
                        logger.info("周末休市，监控暂停")
                        # 计算到下周一9:15的时间
                        days_until_monday = 7 - now.weekday()
                        next_open = (now + timedelta(days=days_until_monday)).replace(
                            hour=9, minute=15, second=0, microsecond=0
                        )
                        sleep_seconds = (next_open - now).total_seconds()
                        logger.info(f"下次开市: {next_open.strftime('%Y-%m-%d %H:%M')}")
                        time.sleep(min(sleep_seconds, 3600))  # 最多睡1小时再检查
                    else:
                        # 非交易时段，每小时检查一次
                        logger.info("非交易时段，每小时检查")
                        time.sleep(3600)
                    continue
                
                # 执行检查
                next_interval = self.run_check()
                
                # 等待下次检查
                time.sleep(next_interval)
                
            except KeyboardInterrupt:
                logger.info("监控被手动停止")
                break
            except Exception as e:
                logger.error(f"运行错误: {e}", exc_info=True)
                time.sleep(60)  # 出错后1分钟重试
        
        # 保存最终状态
        self.save_state()
        logger.info("监控已停止")

if __name__ == "__main__":
    monitor = VolatilityMonitor()
    monitor.run()
