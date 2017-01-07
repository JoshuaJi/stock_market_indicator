from sklearn import svm
import tushare as ts
import pandas as pd
import numpy as np

def sk_predict(df_data):
	df = df_data
	features = []
	targets = []
	for x in xrange(0,df.shape[0]-21):
		features.append(np.array(df['close'][::-1][x:x+20]))
		if df['close'][::-1][x+21] > df['close'][::-1][x+20]:
			targets.append(1)
		else:
			targets.append(-1)
		

	features = np.array(features)
	targets = np.array(targets)

	clf = svm.SVC()
	clf.fit(features, targets)

	return clf.predict(np.array(df['close'][::-1][-21:-1])) == (df['close'][::-1][-1] > df['close'][::-1][-2])