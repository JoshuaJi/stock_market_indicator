import pandas as pd
import datetime
from pandas_datareader import data, wb
from sklearn.svm import SVR

def grab_data(code):
	price_list = data.DataReader(code, 'yahoo')
	return price_list

def train_model(price_list, total_dates, window):
	features = []
	targets = []
	for x in xrange(total_dates-window):
		# print x
		features.append(price_list['Adj Close'][-(total_dates-x):-(total_dates-x)+window].tolist())
		targets.append(price_list['Adj Close'][-(total_dates-x)+window])
	
	model = SVR(kernel='rbf', C=1e3, gamma=0.0001)
	model.fit(features, targets)
	return model

def main():
	window = 15
	total_dates = 300
	price_list = grab_data('601011.ss')
	print price_list[-300:]
	model = train_model(price_list[:-1], total_dates, window)
	print model.predict(price_list['Adj Close'][-window:].tolist())


if __name__ == '__main__':
	main()