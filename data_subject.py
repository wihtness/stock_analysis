import akshare as ak
import pandas as pd
from tqdm import tqdm  # 进度条工具（可选，需安装）

# 1. 获取所有行业板块及成分股
def get_industry_mapping():
    # 获取行业板块列表
    industry_list = ak.stock_board_industry_name_em()
    industry_mapping = pd.DataFrame()
    for index, row in tqdm(industry_list.iterrows(), desc="正在获取行业板块"):
        code = row["板块代码"]
        name = row["板块名称"]
        try:
            # 获取单个行业板块的成分股
            df = ak.stock_board_industry_cons_em(symbol=code)
            df["板块类型"] = "行业板块"
            df["板块名称"] = name
            industry_mapping = pd.concat([industry_mapping, df])
        except Exception as e:
            print(f"获取行业板块 {name}({code}) 失败: {e}")
    return industry_mapping

def get_concept_mapping():
    concept_list = ak.stock_board_concept_name_em()
    concept_mapping = pd.DataFrame()
    for index, row in tqdm(concept_list.iterrows(), total=len(concept_list), desc="正在获取概念题材"):
        code = row["板块代码"]
        name = row["板块名称"]
        try:
            # 获取概念板块成分股
            df = ak.stock_board_concept_cons_em(symbol=code)
            # 检查返回数据是否为空
            if df.empty:
                print(f"\n概念板块 {name}({code}) 无成分股数据，已跳过")
                continue
            # 数据清洗
            df["板块类型"] = "概念题材"
            df["板块名称"] = name
            concept_mapping = pd.concat([concept_mapping, df])
        except Exception as e:
            print(f"\n获取概念板块 {name}({code}) 失败: {str(e)}")
    return concept_mapping

# 重新运行修复后的函数
concept_df = get_concept_mapping()

if __name__ == "__main__":
    # 5. 打印结果示例
    print("股票数量:", len(concept_df))
    print(concept_df.head())