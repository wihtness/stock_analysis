import akshare as ak
import pandas as pd

def fetch_stock_info():
    """
    获取A股股票的基本信息
    """
    stock_info = ak.stock_info_a_code_name()
    return stock_info

def fetch_stock_history_data(stock_code, start_date="20230101", end_date="20231231"):
    """
    获取指定股票的历史交易数据
    :param stock_code: 股票代码，例如 '000001'
    :param start_date: 开始日期，格式为 'YYYYMMDD'
    :param end_date: 结束日期，格式为 'YYYYMMDD'
    """
    stock_history_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date)
    return stock_history_data

if __name__ == "__main__":
    # 获取A股股票的基本信息
    stock_info = fetch_stock_info()
    print("A股股票基本信息:")
    print(stock_info.head())

    # 获取指定股票的历史交易数据
    stock_code = '000001'  # 例如：平安银行
    stock_history_data = fetch_stock_history_data(stock_code)
    print(f"\n{stock_code}的历史交易数据:")
    print(stock_history_data.head())
