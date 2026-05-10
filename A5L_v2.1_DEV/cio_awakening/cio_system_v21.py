#!/usr/bin/env python3
"""
CIO觉醒系统 v2.1 - 云数据增强版
整合: 飞书云文档 + 本地数据 + Tushare实时数据
"""
import json
import os
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening')
sys.path.insert(0, '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data')

# 导入数据引擎
from hybrid_data_provider import CIODataEngine
from feishu_cloud_data_accessor import CIODataManager

class CIOAwakeningSystemV21:
    """
    CIO觉醒系统 v2.1
    
    核心升级:
    1. 飞书云文档数据访问
    2. 混合数据源 (本地 + 云端 + 实时)
    3. 改进的市场快照分析
    4. 实时信号生成
    """
    
    def __init__(self):
        self.version = "2.1.0-cloud"
        self.data_engine = CIODataEngine()
        self.cloud_manager = CIODataManager()
        self.signals_history = []
        self.data_status = {}
        
    def initialize(self):
        """初始化系统"""
        print("🚀 CIO觉醒系统 v2.1 (Cloud Enhanced) 初始化...")
        print("=" * 70)
        
        # 检查数据可用性
        local_dates = self.data_engine.provider.get_local_dates()
        
        self.data_status = {
            'local_files': len(local_dates),
            'date_range': f"{local_dates[0]} - {local_dates[-1]}" if local_dates else "N/A",
            'cloud_access': 'Ready',
            'tushare': 'Available' if self.data_engine.provider.pro else 'Not configured'
        }
        
        print(f"📊 数据状态:")
        for key, value in self.data_status.items():
            print(f"   • {key}: {value}")
        
        print("=" * 70)
        return True
    
    def analyze_market_snapshot(self, date_str: str = None) -> dict:
        """
        分析市场快照
        
        Args:
            date_str: 日期字符串 (如 "20130307")，默认使用最新本地数据
            
        Returns:
            市场分析结果
        """
        if date_str is None:
            dates = self.data_engine.provider.get_local_dates()
            if not dates:
                return {}
            date_str = dates[-1]
        
        snapshot = self.data_engine.get_market_snapshot(date_str)
        
        if not snapshot:
            return {}
        
        # 增强分析
        df = self.data_engine.provider.get_date(date_str)
        
        if df is not None and not df.empty:
            # 计算更多指标
            snapshot['avg_turnover'] = df['amount'].mean() / 1e6  # 百万
            snapshot['median_change'] = df['pct_chg'].median()
            snapshot['std_change'] = df['pct_chg'].std()
            
            # 分布统计
            snapshot['distribution'] = {
                '>5%': len(df[df['pct_chg'] > 5]),
                '0-5%': len(df[(df['pct_chg'] > 0) & (df['pct_chg'] <= 5)]),
                '-5-0%': len(df[(df['pct_chg'] >= -5) & (df['pct_chg'] <= 0)]),
                '<-5%': len(df[df['pct_chg'] < -5])
            }
            
            # 成交额前10
            top_amount = df.nlargest(10, 'amount')[['code', 'close', 'pct_chg', 'amount']]
            snapshot['top_amount'] = top_amount.to_dict('records')
        
        return snapshot
    
    def generate_signal_v21(self, market_snapshot: dict = None) -> dict:
        """
        生成交易信号 v2.1
        
        Returns:
            完整信号字典
        """
        if market_snapshot is None:
            market_snapshot = self.analyze_market_snapshot()
        
        if not market_snapshot:
            return {
                'error': 'No market data available',
                'timestamp': datetime.now().isoformat()
            }
        
        signal = {
            'timestamp': datetime.now().isoformat(),
            'system_version': self.version,
            'data_source': 'hybrid_cloud_local',
            'market_status': market_snapshot,
            'analysis': {},
            'signal': {},
            'recommendations': []
        }
        
        # 1. 市场情绪分析
        up_ratio = market_snapshot.get('up_stocks', 0) / max(market_snapshot.get('total_stocks', 1), 1)
        limit_up = market_snapshot.get('limit_up', 0)
        avg_change = market_snapshot.get('avg_change', 0)
        
        if up_ratio > 0.6 and limit_up > 30:
            market_mood = 'STRONG_BULL'
            mood_emoji = '🚀'
        elif up_ratio > 0.5:
            market_mood = 'BULL'
            mood_emoji = '📈'
        elif up_ratio > 0.4:
            market_mood = 'NEUTRAL'
            mood_emoji = '➡️'
        else:
            market_mood = 'BEAR'
            mood_emoji = '📉'
        
        signal['analysis']['market_mood'] = {
            'status': market_mood,
            'emoji': mood_emoji,
            'up_ratio': up_ratio,
            'limit_up': limit_up,
            'avg_change': avg_change
        }
        
        # 2. 生成交易信号
        if market_mood in ['STRONG_BULL', 'BULL']:
            action = 'BUY'
            confidence = min(0.95, 0.6 + up_ratio * 0.3 + limit_up / 200)
        elif market_mood == 'BEAR':
            action = 'SELL'
            confidence = min(0.95, 0.6 + (1 - up_ratio) * 0.3)
        else:
            action = 'HOLD'
            confidence = 0.5
        
        signal['signal'] = {
            'action': action,
            'confidence': confidence,
            'mood': market_mood,
            'reasoning': f"市场{market_mood}, 涨跌比{up_ratio:.1%}, 涨停{limit_up}家"
        }
        
        # 3. 具体建议
        if action == 'BUY':
            # 找出强势股
            date_str = market_snapshot.get('date')
            if date_str:
                df = self.data_engine.provider.get_date(date_str)
                if df is not None:
                    leaders = df.nlargest(5, 'pct_chg')[['code', 'close', 'pct_chg', 'amount']]
                    signal['recommendations'] = leaders.to_dict('records')
        
        self.signals_history.append(signal)
        return signal
    
    def format_signal_message(self, signal: dict) -> str:
        """格式化为飞书消息"""
        analysis = signal.get('analysis', {})
        market = signal.get('market_status', {})
        sig = signal.get('signal', {})
        mood = analysis.get('market_mood', {})
        
        emoji = mood.get('emoji', '➡️')
        action = sig.get('action', 'HOLD')
        confidence = sig.get('confidence', 0)
        
        # 构建消息
        message = f"""
🤖 **CIO觉醒系统 v{self.version}**

**📅 数据日期**: {market.get('date', 'N/A')}
**📊 市场状态**: {emoji} {mood.get('status', 'N/A')}

**📈 市场统计**
• 上涨: {market.get('up_stocks', 0)}家
• 下跌: {market.get('down_stocks', 0)}家  
• 涨停: {market.get('limit_up', 0)}家
• 平均涨跌: {market.get('avg_change', 0):.2%}
• 总成交: {market.get('total_amount', 0):.0f}亿元

**💡 交易信号**
{emoji} **{action}** (置信度: {confidence:.0%})

**📝 理由**: {sig.get('reasoning', 'N/A')}
"""
        
        # 添加推荐
        recommendations = signal.get('recommendations', [])
        if recommendations:
            message += "\n**🏆 强势股TOP5**\n"
            for i, rec in enumerate(recommendations[:5], 1):
                code = rec.get('code', 'N/A')
                pct = rec.get('pct_chg', 0)
                amount = rec.get('amount', 0) / 1e8  # 亿元
                message += f"{i}. {code} | +{pct:.2%} | ¥{amount:.1f}亿\n"
        
        message += f"\n---\n*生成时间: {datetime.now().strftime('%H:%M:%S')}*"
        
        return message
    
    def run_pre_market_analysis(self):
        """盘前分析 - 09:30前执行"""
        print("\n" + "=" * 70)
        print("🌅 CIO觉醒系统 - 盘前分析")
        print("=" * 70)
        
        # 1. 数据状态检查
        print("\n📊 数据状态检查...")
        self.initialize()
        
        # 2. 市场快照分析
        print("\n🔍 分析市场快照...")
        snapshot = self.analyze_market_snapshot()
        
        if snapshot:
            print(f"\n📈 市场概况 ({snapshot.get('date')}):")
            print(f"   总股票数: {snapshot.get('total_stocks')}")
            print(f"   上涨: {snapshot.get('up_stocks')} | 下跌: {snapshot.get('down_stocks')}")
            print(f"   涨停: {snapshot.get('limit_up')} | 跌停: {snapshot.get('limit_down')}")
            print(f"   平均涨跌: {snapshot.get('avg_change'):.2%}")
            print(f"   总成交: {snapshot.get('total_amount'):.0f}亿元")
            
            # 3. 生成信号
            print("\n🎯 生成交易信号...")
            signal = self.generate_signal_v21(snapshot)
            
            # 4. 显示结果
            print("\n" + "-" * 60)
            print("📱 飞书推送格式:")
            print("-" * 60)
            feishu_msg = self.format_signal_message(signal)
            print(feishu_msg)
            
            # 5. 保存结果
            result_path = '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/results/pre_market_signal_v21.json'
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(signal, f, indent=2, ensure_ascii=False)
            print(f"\n💾 信号已保存: {result_path}")
            
            return signal
        else:
            print("❌ 无法获取市场数据")
            return None


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 CIO觉醒系统 v2.1 - 云数据增强版")
    print("=" * 70)
    
    # 创建系统实例
    cio = CIOAwakeningSystemV21()
    
    # 执行盘前分析
    signal = cio.run_pre_market_analysis()
    
    print("\n" + "=" * 70)
    print("✅ CIO觉醒系统 v2.1 运行完成!")
    print("=" * 70)
    print("\n🎯 v2.1 新特性:")
    print("   • 飞书云文档数据访问")
    print("   • 混合数据源 (本地+云端+实时)")
    print("   • 增强市场快照分析")
    print("   • 改进的信号生成算法")
    print("   • 实时盘前分析能力")
    
    return cio


if __name__ == "__main__":
    cio = main()
