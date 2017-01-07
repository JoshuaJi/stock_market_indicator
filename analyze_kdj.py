import tushare as ts
import pandas as pd
import sys

# classified = pd.read_csv('classified.csv')


def cal_fav_KDJ():
	fav_stocks = []
	classified = ts.get_industry_classified()
	data_size = classified.index.size
	data_period = 9

	for i in xrange(data_size):
		stock = classified.iloc[i]
		data_sample = ts.get_hist_data(stock.code,start='2016-08-01')
		K= 50
		D= 50
		have_K_today = True 

		for x in xrange(0,data_period):
			have_K_today = True 
			try:
				L_n = data_sample[data_period-1-x:2*data_period-1-x].close.min()
				H_n = data_sample[data_period-1-x:2*data_period-1-x].close.max()
				C_n = data_sample.iloc[data_period-1-x].close
				RSV = (C_n - L_n)/(H_n - L_n)*100
				K_last = K
				D_last = D
				K = 2.0/3 * K + 1.0/3 * RSV
				D = 2.0/3 * D + 1.0/3 * K
			except:
				have_K_today = False

		if have_K_today:
			J = 3.0 * K - 2.0 * D
			J_last = 3.0 * K_last - 2.0 * D_last
			#shouldBuy = (J > 100) and (J > D) and (J > K)
			shouldBuy = (J > K) and (K > D) and (K < 20)
			J_slope = J - J_last
			if shouldBuy:
				# print stock	
				# print "K:",K, "  D:", D, "  J:", J
				fav_stocks.append((stock, J_slope, K, D, J))

	fav_stocks.sort(key=lambda x:x[1]) 
	return fav_stocks

def main():

	print cal_fav_KDJ()

if __name__ == '__main__':
	main()

