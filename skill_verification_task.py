import json
from datetime import datetime, timedelta

# 计算日期
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# 第一步：读取昨天的L3预测
try:
    with open(f"data/review_layers/layer3_comprehensive_{yesterday}.json", "r") as f:
        yesterday_report = json.load(f)
    predictions = yesterday_report.get("predictions", {})
except Exception as e:
    print(f"❌ 读取昨天预测报告失败：{str(e)}")
    exit(1)

# 第二步：获取今天的实际数据
try:
    from tools.data_layer import get_data_layer
    data = get_data_layer()
    today_actual = {
        "shanghai_index": data["shanghai_index"],
        "shenzhen_index": data["shenzhen_index"],
        "cyb_index": data["cyb_index"],
        "main_sector": data["sector_rotation"]["main_sector"],
        "sentiment_score": data["sentiment_temp"]["score"]
    }
except Exception as e:
    print(f"❌ 获取今日市场数据失败：{str(e)}")
    exit(1)

# 第三步：验证预测准确度
verification_results = {}

# 验证浪主指数
if "langzhu" in predictions:
    predicted_direction = predictions["langzhu"]["direction"]
    actual_change = today_actual["shanghai_index"]["change"]
    
    if predicted_direction == "看多" and actual_change > 0:
        result = "✅ 准确"
    elif predicted_direction == "看空" and actual_change < 0:
        result = "✅ 准确"
    else:
        result = "❌ 不准确"
    
    verification_results["langzhu"] = {
        "prediction": predicted_direction,
        "actual": actual_change,
        "result": result
    }

# 验证巴菲特情绪
if "buffett" in predictions:
    predicted_divergence = predictions["buffett"]["divergence"]
    # 使用情绪得分判断分歧度
    if predicted_divergence == "low" and today_actual["sentiment_score"] < 30:
        result = "✅ 准确"
    elif predicted_divergence == "high" and today_actual["sentiment_score"] > 70:
        result = "✅ 准确"
    else:
        result = "⚠️ 部分准确"
    
    verification_results["buffett"] = {
        "prediction": predicted_divergence,
        "actual": today_actual["sentiment_score"],
        "result": result
    }

# 验证因子投资
if "factor" in predictions:
    predicted_style = predictions["factor"]["style"]
    actual_main_sector = today_actual["main_sector"]
    
    # 判断是否匹配
    if predicted_style == "成长" and actual_main_sector in ["科技", "半导体", "新能源"]:
        result = "✅ 准确"
    elif predicted_style == "价值" and actual_main_sector in ["银行", "地产", "周期"]:
        result = "✅ 准确"
    else:
        result = "⚠️ 需要调整"
    
    verification_results["factor"] = {
        "prediction": predicted_style,
        "actual": actual_main_sector,
        "result": result
    }

# 第四步：统计准确率
accuracy_stats = {
    "total": len(verification_results),
    "correct": sum(1 for v in verification_results.values() if "✅" in v["result"]),
    "partial": sum(1 for v in verification_results.values() if "⚠️" in v["result"]),
    "incorrect": sum(1 for v in verification_results.values() if "❌" in v["result"])
}

accuracy_rate = accuracy_stats["correct"] / accuracy_stats["total"] * 100 if accuracy_stats["total"] > 0 else 0

# 第五步：生成验证报告
report = f"""📊 【技能预测验证报告】
日期：{today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 浪主指数
- 预测：{predictions['langzhu']['direction']}
- 实际：上证指数{today_actual['shanghai_index']['change']:+.2f}%
- 结果：{verification_results['langzhu']['result']}

🧠 巴菲特情绪
- 预测：分歧度{predictions['buffett']['divergence']}
- 实际：情绪得分{today_actual['sentiment_score']:.0f}
- 结果：{verification_results['buffett']['result']}

📊 因子投资
- 预测：{predictions['factor']['style']}风格
- 实际：主线板块{today_actual['main_sector']}
- 结果：{verification_results['factor']['result']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 综合准确率：{accuracy_rate:.1f}%
- ✅ 准确：{accuracy_stats['correct']}/{accuracy_stats['total']}
- ⚠️ 部分准确：{accuracy_stats['partial']}/{accuracy_stats['total']}
- ❌ 不准确：{accuracy_stats['incorrect']}/{accuracy_stats['total']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 进化建议：
- 连续准确的Skill → 权重+5%
- 连续不准确的Skill → 权重-5%
- 需要调整的Skill → 检查参数
"""

print(report)

# 第六步：保存验证记录
try:
    verification_record = {
        "date": today,
        "predictions_date": yesterday,
        "verification_results": verification_results,
        "accuracy_stats": accuracy_stats,
        "accuracy_rate": accuracy_rate
    }

    with open(f"data/skill_verification_{today}.json", "w") as f:
        json.dump(verification_record, f, indent=2, ensure_ascii=False)

    print(f"✅ 技能验证完成，准确率：{accuracy_rate:.1f}%")
except Exception as e:
    print(f"❌ 保存验证记录失败：{str(e)}")
    exit(1)
