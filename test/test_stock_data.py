import pandas as pd
import unittest

from data_staregy import identify_stock_strategy


class TestIdentifyStockStrategy(unittest.TestCase):
    def setUp(self):
        # 创建一个示例数据帧
        self.data = {
            'date': pd.date_range(start='1/1/2020', periods=100),
            'volume': [1e6] * 100,
            'close': [100] * 100
        }
        self.df = pd.DataFrame(self.data).set_index('date')

    def test_identify_stock_strategy_LowVolumeLowVolatilityHighRecentVolumeHighRecentVolatility(self):
        # 设置条件以满足策略
        self.df.loc['2020-01-01':'2020-01-50', 'volume'] = 5e5  # 低交易量
        self.df.loc['2020-01-01':'2020-01-50', 'close'] = [100 + 0.005 * i for i in range(50)]  # 低波动性
        self.df.loc['2020-01-51':'2020-01-53', 'volume'] = 1e7  # 高近期交易量
        self.df.loc['2020-01-51':'2020-01-53', 'close'] = [100 + 0.05 * i for i in range(3)]  # 高近期波动性

        result = identify_stock_strategy(self.df)
        self.assertTrue(len(result) > 0, "Expected to find stocks matching the strategy")

    def test_identify_stock_strategy_NoStrategyMatch(self):
        # 设置条件以不满足策略
        self.df.loc['2020-01-01':'2020-01-50', 'volume'] = 1e6  # 高交易量
        self.df.loc['2020-01-01':'2020-01-50', 'close'] = [100 + 0.02 * i for i in range(50)]  # 高波动性
        self.df.loc['2020-01-51':'2020-01-53', 'volume'] = 1e6  # 低近期交易量
        self.df.loc['2020-01-51':'2020-01-53', 'close'] = [100 + 0.01 * i for i in range(3)]  # 低近期波动性

        result = identify_stock_strategy(self.df)
        self.assertTrue(len(result) == 0, "Expected no stocks to match the strategy")

    def test_identify_stock_strategy_BoundaryConditions(self):
        # 设置边界条件
        self.df.loc['2020-01-01':'2020-01-50', 'volume'] = 1e6  # 边界交易量
        self.df.loc['2020-01-01':'2020-01-50', 'close'] = [100 + 0.01 * i for i in range(50)]  # 边界波动性
        self.df.loc['2020-01-51':'2020-01-53', 'volume'] = 5e6  # 边界近期交易量
        self.df.loc['2020-01-51':'2020-01-53', 'close'] = [100 + 0.05 * i for i in range(3)]  # 边界近期波动性

        result = identify_stock_strategy(self.df)
        self.assertTrue(len(result) > 0, "Expected to find stocks matching the boundary conditions")

    def test_identify_stock_strategy_JustAboveThresholds(self):
        # 设置条件以略高于阈值
        self.df.loc['2020-01-01':'2020-01-50', 'volume'] = 1.01e6  # 略高于交易量阈值
        self.df.loc['2020-01-01':'2020-01-50', 'close'] = [100 + 0.011 * i for i in range(50)]  # 略高于波动性阈值
        self.df.loc['2020-01-51':'2020-01-53', 'volume'] = 5.01e6  # 略高于近期交易量阈值
        self.df.loc['2020-01-51':'2020-01-53', 'close'] = [100 + 0.051 * i for i in range(3)]  # 略高于近期波动性阈值

        result = identify_stock_strategy(self.df)
        self.assertTrue(len(result) > 0, "Expected to find stocks matching the conditions just above thresholds")


if __name__ == '__main__':
    unittest.main()
