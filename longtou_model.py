"""
接力板模型：跟随资金打造连板
逻辑
	个股首板或二板登上龙虎榜后，若出现知名游资接力买入（如“炒股养家”“宁波桑田路”等席位），可能开启连板行情。本质是资金合力的延续性，需市场情绪和题材强度配合。

选股条件
	个股处于题材主升期，连板数≤3板（过高则风险大）。
	龙虎榜显示买方席位有游资接力（如前一日的买一席位锁仓，新游资大额买入）。
	换手充分（换手率10%-30%），避免缩量加速板（易被砸盘）。
买点与风控
	买点1：次日高开3%-5%，且开盘后分时强势（快速拉升封板）。
	买点2：盘中炸板回封时跟随（需回封速度快、量能稳定）。
"""

"""
涨停低开模型：低吸博弈反包

逻辑
	个股因突发利好或资金抢筹涨停，但次日因市场分歧或主力洗盘低开，形成“预期差”，随后资金回流推动反包。需龙虎榜显示主力资金未离场（如买方席位占比高、卖方无大额出货）。

选股条件
	前一日涨停且登上龙虎榜，买方席位净买入占比＞20%（说明主力主导涨停）。
	次日低开2%-5%（低开太多则弱势，太少则洗盘不充分）。
	题材有持续性（如政策利好、行业风口）。
买点与风控
	买点1：集合竞价低开后，开盘5分钟内快速翻红时介入。
	买点2：分时回踩均线不破，且成交量温和放大时低吸。
"""
