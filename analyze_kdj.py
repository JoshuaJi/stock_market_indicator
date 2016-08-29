import tushare as ts

classified = ts.get_industry_classified()
data_period = 9
data_size = 2837

def cal_KDJ(stock):
	data_sample = ts.get_hist_data(stock.code,start='2016-08-01',end='2016-08-26')

	L_n = data_sample[:data_period].close.min()
	H_n = data_sample[:data_period].close.max()

	K= 50
	D= 50

	have_K_today = True 

	for x in xrange(0,data_period):
		have_K_today = True 
		try:
			C_n = data_sample.iloc[data_period-1-x].close
			RSV = (C_n - L_n)/(H_n - L_n)*100
			K = 2.0/3 * K + 1.0/3 * RSV
			D = 2.0/3 * D + 1.0/3 * K
		except:
			have_K_today = False

	if have_K_today:
		#J = 3.0 * K - 2.0 * D
		#shouldBuy = (J > 100) and (J > D) and (J > K)
		shouldBuy = (K > D) and (K < 30)
		if shouldBuy:
			print stock	
			print "K:",K, "  D:", D, "  J:",J

def main():

	for i in xrange(data_size):
		stock = classified.iloc[i]
		cal_KDJ(stock)


if __name__ == '__main__':
	main()

