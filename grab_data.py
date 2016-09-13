import tushare as ts

df = ts.get_stock_basics()
for code in df.index:
	try:
		price_list = ts.get_hist_data(code)
		price_list.to_csv('/Users/xuji/Desktop/home_automation/stock_market_indicator/data/'+code+'.csv')
	except:
		print code, " doesn't have data yet"