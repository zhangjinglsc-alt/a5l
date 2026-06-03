import akshare as ak
import pandas as pd

# 股票列表
stocks = ["601975", "000066", "688981", "002436", "300708"]

try:
    # 获取全部A股实时行情
    df = ak.stock_zh_a_spot_em()
    # 筛选目标股票
    result = df[df["代码"].isin(stocks)][["代码", "名称", "最新价", "涨跌幅"]]
    print("个股行情结果:")
    print(result.to_markdown(index=False))
except Exception as e:
    print(f"获取行情失败: {e}")
