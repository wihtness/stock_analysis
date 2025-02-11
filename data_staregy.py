import pandas as pd

"""
    检测股票在过去多个交易日内是否符合交易量和股价波动不大，但最近两三个交易日内突增交易量的条件。

    参数:
    stock_data (pd.DataFrame): 包含股票历史交易数据的 DataFrame，字段包括 'code', 'open', 'close', 'high', 'low', 'volume', 'date' 等。
    quiet_days (int): 用于判断交易量和价格波动较小的天数。
    recent_days (int): 检查最近几天突增交易量的天数。
    volume_threshold (float): 最近几天交易量相较于平均值的放大倍数（默认 2 倍）。
    price_change_threshold (float): 用于判断股价波动小的阈值（默认 2%，即 0.02）。

    返回:
    bool: 如果符合条件返回 True，否则返回 False。
"""
def detect_volume_spike(stock_data, quiet_days=10, recent_days=3, volume_threshold=2, price_change_threshold=0.02):

    stock_data = pd.DataFrame(stock_data)  # 确保stock_data是一个DataFrame
    stock_data = stock_data.sort_values(by='date')

    # --- 1. 计算过去 quiet_days 的平均交易量和价格波动 ---
    # 过去 quiet_days 的数据
    quiet_data = stock_data.iloc[-(quiet_days + recent_days):-recent_days]

    if quiet_data.empty or len(quiet_data) < quiet_days:
        raise ValueError("历史数据不足以计算安静期的统计指标")

    # 计算平均交易量
    avg_volume_quiet = quiet_data['volume'].mean()

    # 计算股价波动（振幅 = (最高 - 最低) / 收盘）
    avg_price_change_quiet = ((quiet_data['high'] - quiet_data['low']) / quiet_data['close']).mean()

    # --- 2. 检查过去 quiet_days 是否符合波动和交易量较小的条件 ---
    if avg_price_change_quiet > price_change_threshold:
        return False  # 过去的价格波动太大
    if quiet_data['volume'].std() > avg_volume_quiet * 0.5:  # 交易量波动也较大
        return False

    # --- 3. 检测最近 recent_days 是否出现交易量突增 ---
    recent_data = stock_data.iloc[-recent_days:]
    if recent_data.empty or len(recent_data) < recent_days:
        raise ValueError("最近数据不足以检测交易量突增")

    # 检查最近几天的交易量是否显著高于平均交易量
    recent_volume_spike = recent_data['volume'].mean() > avg_volume_quiet * volume_threshold

    # 检查最近几天是否有显著的股价波动
    recent_price_change_spike = ((recent_data['high'] - recent_data['low']) / recent_data['close']).mean() > price_change_threshold

    # 如果最近几天交易量突增并且波动增加，返回 True
    return recent_volume_spike and recent_price_change_spike


"""
    股票价格估计函数
"""

"""
    股票题材标签
        标签更新事件
"""

"""
    题材热度--热门题材--（联合证券数据、研究数据）
        下属股票--
        数据来源及可信度分析
        股票评级
"""

"""
    股票评级函数
        买入评价
            一级：
            二级：
            三级：
"""

"""
    零散数据整理函数：
        整理题材消息面
            地区新政策
            地区焦点事件
            行业/企业经营活动公告
"""
