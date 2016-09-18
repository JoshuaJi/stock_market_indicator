import os, sys
import tushare as ts
import pandas as pd
import datetime
from pandas_datareader import data, wb

def Format_api_code(code):
	if code[0] == '6':
		return code + ".ss"
	else:
		return code + ".sz"

def Redownload_All_Csv(df):
	for code in df.index:
		api_code = Format_api_code(code)
		try:
			price_list = data.DataReader(api_code, 'yahoo')
			price_list.to_csv(base_dir+code+'.csv')
		except:
			print code, "reset: doesn't have data yet"

def main():
	base_dir = '/home/joshua/Desktop/smart_home/stock_market_indicator/data_yahoo/'
	df = ts.get_stock_basics()
	if sys.argv[1] == "update":
		for code in df.index:
			file_path = base_dir+code+'.csv'
			api_code = Format_api_code(code)
			
			if (os.path.isfile(file_path)):
				price_list = pd.read_csv(base_dir+code+'.csv', index_col = 0)
				end_date = price_list.iloc[-1].name
				try:
					end_date = end_date.split('-')
					end_date = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
					patch_start_date = end_date + datetime.timedelta(1)
				except:
					print 'split error: ', code, end_date, type(end_date)
				try:
					price_patch = data.DataReader(api_code, 'yahoo', start=patch_start_date)
					price_list = price_list.append(price_patch)
					price_list.to_csv(file_path)
				except:
					print code, "is already up to date"

			else:
				try:
					price_list = data.DataReader(api_code, 'yahoo')
					price_list.to_csv(file_path)
				except:
					print code, "update: doesn't have data yet"
	
	elif sys.argv[1] == "redownload":
		Redownload_All_Csv(df)

	else:
		print "please use [update] or [redownload] as option"



if __name__ == '__main__':
	main()