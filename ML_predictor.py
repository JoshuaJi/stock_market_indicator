import pandas as pd
import datetime
from pandas_datareader import data, wb
from sklearn.svm import SVR

# logging
num_correct = 0
num_incorrect = 0

def grab_data(code):
	price_list = data.DataReader(code, 'yahoo')
	return price_list

def train_model(price_list, total_dates, window, future_days):
	features = []
	targets = []
	for x in xrange(total_dates-window-future_days+1):
		features.append(price_list['Adj Close'][-(total_dates-x):-(total_dates-x)+window].tolist())
		targets.append(price_list['Adj Close'][-(total_dates-x)+window+future_days-1])
	
	model = SVR(kernel='rbf', C=1e3, gamma=0.0001)
	model.fit(features, targets)
	return model

def predict_price(code, total_dates, window, future_days):
	global num_correct
	global num_incorrect

	price_list = grab_data(code)
	# print price_list[-total_dates:]
	# print price_list['Adj Close'][-future_days-1]
	try:
		model = train_model(price_list[:-future_days], total_dates, window, future_days)
		prediction = model.predict(price_list['Adj Close'][-window:].reshape((1, -1)))
	except:
		return

	print "p: " + str(prediction)
	print "r: " + str(price_list['Adj Close'][-1])
	if ((prediction>price_list['Adj Close'][-2]) == (price_list['Adj Close'][-1]>price_list['Adj Close'][-2])):
		is_correct = 'correct'
		num_correct = num_correct+1
	else:
		is_correct = 'incorrect'
		num_incorrect = num_incorrect+1
	print "prediction is: " + is_correct
	print "===================="

def main():
	window = 5
	total_dates = 300

	# 1 stands for tomorrow
	future_days = 1

	company_list = pd.read_csv('companylist-2.csv')
	# for code in company_list.Symbol:
	# 	predict_price(code, total_dates, window, future_days)

	predict_price('BABA', total_dates, window, future_days)

	print "number of correct is: " + str(num_correct)
	print "number of incorrect is: " + str(num_incorrect)

if __name__ == '__main__':
	main()