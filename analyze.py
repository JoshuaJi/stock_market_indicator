import tushare as ts

classified = ts.get_industry_classified()
data_size = 2840

for i in xrange(data_size):
	try:
	        stock = classified.loc[i]
		data_sample = ts.get_hist_data(stock.code,start='2016-08-01',end='2016-08-26')
		shouldBuy = (data_sample[:5].close.mean() < data_sample[:20].close.mean()*0.9)
		if shouldBuy:
			print stock
	except:
		print i
