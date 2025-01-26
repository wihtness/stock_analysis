import pandas as pd

# 从 CSV 文件读取数据
df = pd.read_csv(r'C:\Users\limin\Desktop\openai\biga\data.csv')


print(df.head())

# 显示后几行数据
print(df.tail())# 选择特定列
selected_columns = df[['日期', '开盘', '收盘']]

# 选择特定行
selected_rows = df[df['日期'] > '2024-01-01']# 删除缺失值
df_cleaned = df.dropna()

# 填充缺失值
df_filled = df.fillna(0)# 将字符串转换为日期时间类型
df['日期'] = pd.to_datetime(df['日期'])

# 重命名列
df.rename(columns={'开盘': 'Open'}, inplace=True)# 按照特定列进行分组并计算平均值
grouped_data = df.groupby('日期').mean()# 按照特定列进行排序
sorted_data = df.sort_values(by='收盘', ascending=False)# 合并两个 DataFrame
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'C': [7, 8]})
merged_df = pd.merge(df1, df2, on='A')

import matplotlib.pyplot as plt

# 绘制柱状图
df.plot(kind='bar', x='日期', y='收盘')
plt.show()