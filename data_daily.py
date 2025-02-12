from config import db_config

import akshare as ak
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import mplfinance as mpf
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine, text


"""
    使用akshare库获取指定股票的历史数据

    :param stock_code: 股票代码，例如 '000001'
    :param start_date: 开始日期，格式为 'YYYYMMDD'
    :param end_date: 结束日期，格式为 'YYYYMMDD'
    :return: 股票历史数据的DataFrame
    """
def fetch_stock_data(stock_code, start_date, end_date):

    try:
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        return stock_zh_a_hist_df
    except Exception as e:
        print(f"An error occurred while fetching stock data for {stock_code}: {e}")
        return pd.DataFrame()


# 1. 获取上交所主板股票代码（代码以60开头，科创板除外）
def get_sh_main_board():
    df_sh = ak.stock_info_sh_name_code()
    # 筛选主板：证券代码以60开头，排除300、688、43、83、87、88开头的股票
    # df_sh_main = df_sh[~df_sh['证券代码'].str.startswith(('300', '688', '43', '83', '87', '88')) & df_sh['证券代码'].str.startswith('60')]
    df_sh_main = df_sh
    return df_sh_main[['证券代码', '证券简称']]

# 2. 获取深交所主板股票代码（代码以000、001开头）
def get_sz_main_board():
    df_sz = ak.stock_info_sz_name_code(symbol="A股列表")
    # 筛选主板：证券代码以000或001开头
    # df_sz_main = df_sz[df_sz['A股代码'].astype(str).str.match('^000|^001')]
    # df_sz_main = df_sz[~df_sz['A股代码'].str.startswith(('300', '688', '43', '83', '87', '88')) & df_sz['A股代码'].str.startswith('60')]
    df_sz_main = df_sz
    return df_sz_main[['A股代码', 'A股简称']]




def format_data(df):
    # 确保DataFrame的索引是日期时间类型
    df['日期'] = pd.to_datetime(df['日期'])

    # 把日期+股票代码
    df['id'] = df['日期'].dt.strftime('%Y%m%d') + '_' + df['股票代码']

    df.index = df['id']

    # 重命名列以符合mplfinance的要求
    df.rename(columns={'股票代码': 'code','开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'
        , '成交额': 'volumeM', '振幅': 'zhenfu', '涨跌幅': 'zhangde', '换手率': 'huanshou', '涨跌额': 'zhangdeM', '日期': 'date'}, inplace=True)



def write_to_mysql(df, table_name, db_config):
    # 修改连接字符串以指定身份验证插件
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    with engine.connect() as connection:
        # 使用参数化查询来避免SQL注入


        sql = text(f"""
            INSERT INTO {table_name} (id, code, date, open, close, high, low, volume, volumeM, zhenfu, zhangde, huanshou, zhangdeM)
            VALUES (:id, :code, :date, :open, :close, :high, :low, :volume, :volumeM, :zhenfu, :zhangde, :huanshou, :zhangdeM)
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
        """)

        # 使用字典形式的参数
        params_dict = [
            {
                'id': row['id'], 'code': row['code'], 'date': row['date'], 'open': row['open'],
                'close': row['close'], 'high': row['high'], 'low': row['low'], 'volume': row['volume'],
                'volumeM': row['volumeM'], 'zhenfu': row['zhenfu'], 'zhangde': row['zhangde'],
                'huanshou': row['huanshou'], 'zhangdeM': row['zhangdeM']
            }
            for index, row in df.iterrows()
        ]

        try:
            connection.execute(sql, params_dict)
            connection.commit()
            # result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            # if result == len(df):
            #     print("All data verified successfully.")
            # else:
            #     print(f"Verification failed: {result} out of {len(df)} rows inserted.")
        except Exception as e:
            print(f"An error occurred: {e}")


def sync_data(stock_codes):
    # stock_codes = ["600519", "000001", "601318"]  # 添加更多股票代码
    start_date = "20250207"
    end_date = "20250211"


    for index, stock_code in enumerate(stock_codes):
        data = fetch_stock_data(stock_code, start_date, end_date)

        #控制台输出下载下来的data数据长度
        print(f"Downloaded {len(data)} rows for stock {stock_code}")

        if data.empty:
            print(f"No data found for stock {stock_code}")
            continue

        format_data(data)

        # 将数据写入MySQL数据库
        write_to_mysql(data, 'stock_data', db_config)

        # 输出进度
        print(f"Processed {index + 1}/{len(stock_codes)} stocks: {stock_code}")


def getAllCode():
    df_main_board = pd.concat([
        get_sh_main_board().rename(columns={'证券代码': '代码', '证券简称': '简称'}),
        get_sz_main_board().rename(columns={'A股代码': '代码', 'A股简称': '简称'})
    ], ignore_index=True)

    print(df_main_board)

    #存入csv文件中
    df_main_board.to_csv('stock_list.csv', index=False)


def sync_data():
    # 读取stock_list.csv数据
    df = pd.read_csv('data/stock_list.csv', dtype={'代码': str})  # 指定'代码'列为字符串类型
    # 把第一列股票代码放到列表
    stock_codes = df['代码'].tolist()
    sync_data(stock_codes)

if __name__ == "__main__":
    sync_data()
