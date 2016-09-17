import tushare as ts
from pandas_datareader import data, wb

df = ts.get_stock_basics()
for code in df.index:
	try:
		if code[0] == '6':
			api_code = code + ".ss"
		else:
			api_code = code + ".sz"

		price_list = data.DataReader(api_code, 'yahoo')
		price_list.to_csv('/home/joshua/Desktop/smart_home/stock_market_indicator/data_yahoo/'+code+'.csv')
	except:
		print code, " doesn't have data yet"
