#!/usr/bin/env python3
"""
Codex - 代码生成与策略编程助手 v1.0.0
将投资逻辑转化为可执行代码

用法:
    python3 -m codex strategy "描述" --output file.py
    python3 -m codex backtest strategy.py --period start:end
    python3 -m codex monitor SYMBOL --condition "..."
    python3 -m codex code "自然语言描述"
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class Codex:
    """Codex代码生成引擎"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = Path(workspace)
        self.codex_dir = self.workspace / "skills/codex"
        self.templates_dir = self.codex_dir / "templates"
        self.output_dir = self.workspace / "strategies/generated"
        
        # 确保目录存在
        self.codex_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化模板
        self._init_templates()
    
    def _init_templates(self):
        """初始化代码模板"""
        self.templates = {
            "strategy": self._strategy_template(),
            "backtest": self._backtest_template(),
            "monitor": self._monitor_template(),
            "data": self._data_analysis_template(),
        }
    
    def _strategy_template(self) -> str:
        """策略代码模板"""
        return '''# {filename}
# 生成时间: {timestamp}
# 策略来源: {source}
# CTF分级: Tier {tier}

from a5l.trading import Strategy, Position
from a5l.risk import CTFPositionSizer

class {class_name}(Strategy):
    """
    {name} ({symbol}) Tier {tier}策略执行器
    
    CTF分级:
    - Tier: {tier} ({tier_name})
    - 仓位上限: {position_limit}%
    - 当前仓位: {current_position}%
    - 触发条件: {trigger_condition}
    """
    
    def __init__(self):
        super().__init__()
        self.symbol = "{symbol}"
        self.name = "{name}"
        self.ctf_tier = {tier}
        self.position_limit = {position_limit_pct}
        self.current_position = {current_position_pct}
        
    def on_market_open(self):
        """开盘前检查"""
        {open_logic}
    
    def on_market_close(self):
        """收盘后操作"""
        {close_logic}
    
    def execute(self):
        """执行策略"""
        {execute_logic}
'''
    
    def _backtest_template(self) -> str:
        """回测框架模板"""
        return '''# {filename}
# 回测框架
# 生成时间: {timestamp}

from a5l.backtest import BacktestEngine
from a5l.data import StockData
from strategies.{strategy_module} import {strategy_class}

class {backtest_class}:
    """
    {name} Tier {tier}策略回测
    
    回测区间: {start_date} 至 {end_date}
    初始资金: ¥{initial_capital:,}
    策略: {strategy_description}
    """
    
    def __init__(self):
        self.engine = BacktestEngine(
            initial_capital={initial_capital},
            start_date="{start_date}",
            end_date="{end_date}",
            commission={commission}
        )
        self.strategy = {strategy_class}()
        self.data = StockData.load("{symbol}")
    
    def run(self):
        """执行回测"""
        print("开始回测...")
        results = self.engine.run(
            strategy=self.strategy,
            data=self.data
        )
        
        print(f"\\n回测结果:")
        print(f"  总收益率: {{results.total_return:.2%}}")
        print(f"  最大回撤: {{results.max_drawdown:.2%}}")
        print(f"  夏普比率: {{results.sharpe_ratio:.2f}}")
        print(f"  交易次数: {{results.trade_count}}")
        
        return results

if __name__ == "__main__":
    backtest = {backtest_class}()
    results = backtest.run()
'''
    
    def _monitor_template(self) -> str:
        """监控脚本模板"""
        return '''# {filename}
# 监控脚本
# 生成时间: {timestamp}

import time
from datetime import datetime
from a5l.market import MarketData
from hermes import Hermes

class {monitor_class}:
    """
    {name} ({symbol}) 监控器
    
    监控逻辑:
    - 标的: {symbol}
    - 条件: {condition}
    - 通知级别: {priority}
    """
    
    def __init__(self):
        self.symbol = "{symbol}"
        self.name = "{name}"
        self.hermes = Hermes()
        print(f"[{datetime.now()}] 监控器初始化: {{self.name}}")
    
    def check_condition(self):
        """检查条件"""
        data = MarketData.get_realtime(self.symbol)
        
        {check_logic}
        
        return False
    
    def run(self, interval={interval}):
        """持续监控"""
        print(f"开始监控 {{self.name}}，每{{interval}}秒检查一次...")
        
        try:
            while True:
                if self.check_condition():
                    print(f"✅ 条件触发，监控结束")
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\\n监控已手动停止")

if __name__ == "__main__":
    monitor = {monitor_class}()
    monitor.run()
'''
    
    def _data_analysis_template(self) -> str:
        """数据分析模板"""
        return '''# {filename}
# 数据分析脚本
# 生成时间: {timestamp}

import pandas as pd
import matplotlib.pyplot as plt
from a5l.data import StockData

class {analysis_class}:
    """
    {name} 数据分析
    
    分析内容:
    - 标的: {symbol}
    - 周期: {period}
    - 指标: {indicators}
    """
    
    def __init__(self):
        self.symbol = "{symbol}"
        self.name = "{name}"
        self.data = StockData.load(self.symbol)
    
    def analyze(self):
        """执行分析"""
        print(f"分析 {{self.name}}...")
        
        {analysis_logic}
        
        return results
    
    def visualize(self, save_path=None):
        """可视化"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        {visualization_logic}
        
        if save_path:
            plt.savefig(save_path)
            print(f"图表已保存: {{save_path}}")
        
        plt.show()

if __name__ == "__main__":
    analyzer = {analysis_class}()
    results = analyzer.analyze()
    analyzer.visualize()
'''
    
    def generate_strategy(self, description: str, **kwargs) -> str:
        """
        生成策略代码
        
        Args:
            description: 策略自然语言描述
            **kwargs: 额外参数
        
        Returns:
            生成的代码字符串
        """
        print(f"📝 Codex: 解析策略描述...")
        
        # 解析描述
        parsed = self._parse_strategy_description(description)
        
        # 准备模板参数
        params = {
            "filename": kwargs.get("filename", f"strategy_{parsed['symbol']}_{datetime.now().strftime('%Y%m%d')}.py"),
            "timestamp": datetime.now().isoformat(),
            "source": kwargs.get("source", "CTF + Chief指令"),
            "class_name": parsed.get("class_name", "GeneratedStrategy"),
            "name": parsed.get("name", "未命名"),
            "symbol": parsed.get("symbol", "000000.SZ"),
            "tier": parsed.get("tier", 2),
            "tier_name": self._tier_name(parsed.get("tier", 2)),
            "position_limit": kwargs.get("position_limit", "20-25"),
            "position_limit_pct": kwargs.get("position_limit_pct", 0.25),
            "current_position": kwargs.get("current_position", "0"),
            "current_position_pct": kwargs.get("current_position_pct", 0.0),
            "trigger_condition": parsed.get("condition", "未指定"),
            "open_logic": self._generate_open_logic(parsed),
            "close_logic": self._generate_close_logic(parsed),
            "execute_logic": self._generate_execute_logic(parsed),
        }
        
        # 生成代码
        code = self.templates["strategy"].format(**params)
        
        # 保存
        if kwargs.get("save", True):
            output_file = self.output_dir / params["filename"]
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ 策略代码已生成: {output_file}")
        
        return code
    
    def _parse_strategy_description(self, description: str) -> Dict:
        """解析策略描述"""
        parsed = {
            "description": description,
        }
        
        # 提取股票代码/名称
        # 简单规则: 匹配 "中国长城" 或 "000066" 或 "000066.SZ"
        name_match = re.search(r'([\u4e00-\u9fa5]{2,6})', description)
        code_match = re.search(r'(\d{6})(?:\.SZ|\.SH)?', description)
        
        if name_match:
            parsed["name"] = name_match.group(1)
            parsed["class_name"] = self._name_to_class(parsed["name"])
        
        if code_match:
            code = code_match.group(1)
            suffix = ".SZ" if code.startswith(("00", "30")) else ".SH"
            parsed["symbol"] = f"{code}{suffix}"
        else:
            parsed["symbol"] = "000000.SZ"
        
        # 提取Tier
        tier_match = re.search(r'Tier\s*(\d)', description, re.IGNORECASE)
        if tier_match:
            parsed["tier"] = int(tier_match.group(1))
        
        # 提取条件
        if "减仓" in description or "卖出" in description:
            parsed["condition"] = "limit_up_broken"
        elif "买入" in description or "建仓" in description:
            parsed["condition"] = "buy_signal"
        else:
            parsed["condition"] = "manual"
        
        return parsed
    
    def _name_to_class(self, name: str) -> str:
        """中文名转类名"""
        # 简化的拼音转换
        mapping = {
            "中国长城": "ChinaGreatWall",
            "盈峰环境": "YingfengEnvironment",
            "招商南油": "ChinaMerchantsEnergy",
        }
        return mapping.get(name, "GeneratedStrategy")
    
    def _tier_name(self, tier: int) -> str:
        """Tier数字转名称"""
        names = {
            1: "范式级",
            2: "周期确认级",
            3: "资金驱动级",
            4: "补涨扩散级",
        }
        return names.get(tier, "未分级")
    
    def _generate_open_logic(self, parsed: Dict) -> str:
        """生成开盘逻辑"""
        condition = parsed.get("condition", "")
        
        if condition == "limit_up_broken":
            return '''# 检查是否连续涨停
if self.is_limit_up(days=4):
    self.plan_reduction(
        from_pct=self.current_position,
        to_pct=self.position_limit,
        method="gradual"
    )'''
        else:
            return "pass  # 无特定开盘逻辑"
    
    def _generate_close_logic(self, parsed: Dict) -> str:
        """生成收盘逻辑"""
        return "pass  # 无特定收盘逻辑"
    
    def _generate_execute_logic(self, parsed: Dict) -> str:
        """生成执行逻辑"""
        condition = parsed.get("condition", "")
        
        if condition == "limit_up_broken":
            return '''if self.check_limit_up_broken():
    self.reduce_position(
        target_pct=self.position_limit,
        urgency="immediate"
    )'''
        else:
            return "pass  # 执行主逻辑"
    
    def natural_to_code(self, description: str) -> str:
        """
        自然语言描述 → Python代码
        
        Args:
            description: 自然语言描述
            
        Returns:
            Python代码
        """
        print(f"📝 Codex: 自然语言转代码...")
        
        # 简单规则匹配
        if "每天" in description and "收盘" in description:
            return self._generate_daily_check_code(description)
        elif "监控" in description:
            return self._generate_monitor_code(description)
        elif "分析" in description:
            return self._generate_analysis_code(description)
        else:
            return f"# TODO: 实现 '{description}'\n# 请提供更详细的逻辑描述"
    
    def _generate_daily_check_code(self, description: str) -> str:
        """生成每日检查代码"""
        return f'''#!/usr/bin/env python3
"""
自动生成脚本
描述: {description}
"""

from datetime import datetime
from a5l.portfolio import Portfolio

class DailyCheck:
    def run(self):
        portfolio = Portfolio.load()
        
        # 检查持仓盈亏
        for pos in portfolio.positions:
            pnl_pct = pos.pnl_percentage
            
            if pnl_pct < -0.05:  # 亏损超过5%
                print(f"⚠️  {{pos.name}} 亏损 {{pnl_pct:.2%}}")
                # 发送警报
                from hermes import Hermes
                Hermes().send(
                    content=f"持仓亏损警报: {{pos.name}} 亏损 {{pnl_pct:.2%}}",
                    priority="P1"
                )

if __name__ == "__main__":
    DailyCheck().run()
'''
    
    def _generate_monitor_code(self, description: str) -> str:
        """生成监控代码"""
        return self.templates["monitor"].format(
            filename="monitor_generated.py",
            timestamp=datetime.now().isoformat(),
            monitor_class="GeneratedMonitor",
            name="未命名",
            symbol="000000.SZ",
            condition="custom",
            priority="P2",
            interval=60,
            check_logic="# 自定义检查逻辑\n        pass"
        )
    
    def _generate_analysis_code(self, description: str) -> str:
        """生成分析代码"""
        return self.templates["data"].format(
            filename="analysis_generated.py",
            timestamp=datetime.now().isoformat(),
            analysis_class="GeneratedAnalysis",
            name="未命名",
            symbol="000000.SZ",
            period="1年",
            indicators="自定义",
            analysis_logic="# 自定义分析逻辑\n        results = {}",
            visualization_logic="# 自定义可视化\n        pass"
        )

def main():
    codex = Codex()
    
    if len(sys.argv) < 2:
        print("""
Codex - 代码生成与策略编程助手

用法:
  python3 -m codex strategy "描述" --output file.py
  python3 -m codex code "自然语言描述"
  python3 -m codex backtest strategy.py
  python3 -m codex monitor SYMBOL --condition "..."
        """)
        return 0
    
    command = sys.argv[1]
    
    if command == "strategy":
        if len(sys.argv) < 3:
            print("❌ 缺少策略描述")
            return 1
        
        description = sys.argv[2]
        output = None
        
        for i, arg in enumerate(sys.argv):
            if arg == "--output" and i + 1 < len(sys.argv):
                output = sys.argv[i + 1]
        
        code = codex.generate_strategy(
            description,
            filename=output or "generated_strategy.py"
        )
        print("\n生成的代码:\n")
        print(code)
        return 0
    
    elif command == "code":
        if len(sys.argv) < 3:
            print("❌ 缺少描述")
            return 1
        
        description = sys.argv[2]
        code = codex.natural_to_code(description)
        print(code)
        return 0
    
    elif command == "backtest":
        print("🔄 回测框架生成 (功能开发中)")
        return 0
    
    elif command == "monitor":
        print("👁️  监控脚本生成 (功能开发中)")
        return 0
    
    else:
        print(f"❌ 未知命令: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
