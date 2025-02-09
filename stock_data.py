
import mplfinance as mpf
import mysql.connector
from mysql.connector import Error


from data_staregy import detect_volume_spike
from config import db_config






def read_from_mysql(table_name, db_config):
    connection = None
    try:
        # 修改连接配置以指定身份验证插件
        connection = mysql.connector.connect(**db_config, auth_plugin='mysql_native_password')
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            cursor.close()
            return data
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
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




if __name__ == "__main__":

    data=read_from_mysql('stock_data', db_config)
    print(data)

    # 绘制K线图和量能图
    #plot_kline_and_volume(data)

    # 应用策略
    result = detect_volume_spike(data)
    print("该股票是否符合条件：", result)


