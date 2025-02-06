import akshare as ak
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import mplfinance as mpf
import mysql.connector
from mysql.connector import Error
import sqlalchemy  # 添加: 导入sqlalchemy模块
import cryptography  # 添加对 cryptography 包的导入


def fetch_stock_data(stock_code, start_date, end_date):
    """
    使用akshare库获取指定股票的历史数据

    :param stock_code: 股票代码，例如 '000001'
    :param start_date: 开始日期，格式为 'YYYYMMDD'
    :param end_date: 结束日期，格式为 'YYYYMMDD'
    :return: 股票历史数据的DataFrame
    """
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="")
    return stock_zh_a_hist_df

def write_to_mysql(df, table_name, db_config):

    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    with engine.connect() as connection:
        # 使用参数化查询来避免SQL注入
        params = [
            (
                row['id'], row['code'], row['date'], row['open'], row['close'], row['high'], row['low'],
                row['volume'], row['volumeM'], row['zhenfu'], row['zhangde'], row['huanshou'], row['zhangdeM']
            )
            for index, row in df.iterrows()
        ]

        sql = f"""
            INSERT INTO {table_name} (id, code, date, open, close, high, low, volume, volumeM, zhenfu, zhangde, huanshou, zhangdeM)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            code=VALUES(code),
            date=VALUES(date),
            open=VALUES(open),
            close=VALUES(close),
            high=VALUES(high),
            low=VALUES(low),
            volume=VALUES(volume),
            volumeM=VALUES(volumeM),
            zhenfu=VALUES(zhenfu),
            zhangde=VALUES(zhangde),
            huanshou=VALUES(huanshou),
            zhangdeM=VALUES(zhangdeM)
        """
        # 修改: 确保 SQL 语句正确
        connection.execute(sql, params)


def read_from_mysql(table_name, db_config):

    
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            cursor.close()
            return data
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def plot_kline_and_volume(df):
    """
    使用mplfinance库绘制K线图和量能图

    :param df: 包含股票历史数据的DataFrame
    """
    
    # 自定义颜色映射
    colors = mpf.make_marketcolors(up='r', down='g', volume='in')
    # mpf_style = mpf.make_mpf_style(marketcolors=colors, base_mpf_style='yahoo', rc={'figure.facecolor': 'white', 'axes.facecolor': 'white'})
    

    # 设置mplfinance的样式
    mpf_style = mpf.make_mpf_style(marketcolors=colors, base_mpf_style='yahoo', rc={'figure.facecolor': 'white', 'axes.facecolor': 'white'})

    # 绘制K线图和量能图
    mpf.plot(df, type='candle', style=mpf_style, volume=True, title='Stock K-line and Volume', ylabel='Price', ylabel_lower='Volume', figratio=(14, 7))


def format_data(df):
     # 确保DataFrame的索引是日期时间类型
    df['日期'] = pd.to_datetime(df['日期'])

    # 把日期+股票代码
    df['id'] = df['日期'].dt.strftime('%Y%m%d') + '_' + df['股票代码']

    df.index = df['id']

    # 重命名列以符合mplfinance的要求
    df.rename(columns={'股票代码': 'code','开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'
                            , '成交额': 'volumeM', '振幅': 'zhenfu', '涨跌幅': 'zhangde', '换手率': 'huanshou', '涨跌额': 'zhangdeM', '日期': 'date'}, inplace=True)
  

def identify_stock_strategy(df, lookback_days=50, recent_days=3, volume_threshold=1e6, price_volatility_threshold=0.01):
    """
    识别符合特定策略的股票代码

    :param df: 包含股票历史数据的DataFrame
    :param lookback_days: 过去多少个交易日
    :param recent_days: 最近多少个交易日
    :param volume_threshold: 交易量阈值
    :param price_volatility_threshold: 价格波动阈值
    :return: 符合策略的股票代码列表
    """
    # 确保DataFrame按日期排序
    df = df.sort_index()

    # 计算过去lookback_days天的平均交易量和价格波动
    df['avg_volume'] = df['volume'].rolling(window=lookback_days).mean()
    df['price_change'] = df['close'].pct_change()
    df['volatility'] = df['price_change'].rolling(window=lookback_days).std()

    # 检查过去lookback_days天的交易量是否较小且价格波动不大
    low_volume_condition = df['avg_volume'] < volume_threshold
    low_volatility_condition = df['volatility'] < price_volatility_threshold

    # 检查最近recent_days天的交易量是否突然放大且价格波动剧烈
    recent_avg_volume = df['volume'].rolling(window=recent_days).mean().shift(-(recent_days-1))
    recent_price_change = df['price_change'].rolling(window=recent_days).std().shift(-(recent_days-1))
    high_recent_volume_condition = recent_avg_volume > volume_threshold * 5
    high_recent_volatility_condition = recent_price_change > price_volatility_threshold * 5

    # 找出符合条件的股票
    strategy_condition = (low_volume_condition & low_volatility_condition & high_recent_volume_condition & high_recent_volatility_condition)
    strategy_stocks = df[strategy_condition]

    return strategy_stocks.index.tolist()


if __name__ == "__main__":
    # 示例：获取多支股票从20241201到20250124的历史数据
    stock_codes = ["600519", "000001", "601318"]  # 添加更多股票代码
    start_date = "20241201"
    end_date = "20250124"

    # 数据库配置信息
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'port': '3306',
        'password': 'helowin',
        'database': 'biga'
    }

    for stock_code in stock_codes:
        data = fetch_stock_data(stock_code, start_date, end_date)
        print(data)

        format_data(data)

        # 将数据写入MySQL数据库
        write_to_mysql(data, 'stock_data', db_config)

    # 绘制K线图和量能图
    #plot_kline_and_volume(data)

    # 应用策略
    # strategy_stocks = identify_stock_strategy(data)
    # print("符合策略的股票代码:", strategy_stocks)
