import akshare as ak
import time

print("测试AKShare A股实时行情接口...")
try:
    # 测试获取平安银行的实时数据
    df = ak.stock_zh_a_spot_em()
    print(f"✅ 接口调用成功，获取到 {len(df)} 条股票数据")
    print(df.head(3))
except Exception as e:
    print(f"❌ 接口调用失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试获取单只股票数据...")
try:
    df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260601", end_date="20260601")
    print(f"✅ 获取000001数据成功，共 {len(df)} 条")
    print(df)
except Exception as e:
    print(f"❌ 获取000001失败: {e}")