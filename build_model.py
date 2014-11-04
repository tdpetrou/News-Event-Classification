import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestRegressor
import pickle

def read_data():
	'''
	reads data from csv that I generated from copying and pasting articles from
	5 different news sources
	'''
	data = pd.read_csv("prelim_data.csv")
	data['Article'] = data['Article'].apply(lambda x: str(re.sub('[^\w\s]+', '', x)))
	data['Article'] = data['Article'].apply(lambda x: str(re.sub('[\r]+', ' ', x)))
	return data

def get_features(data):
	vec = TfidfVectorizer(stop_words='english')

	X = data['Article'].values
	label = data['source'].values
	y = data['rating']

	test_indices = [0, 5, 10, 15, 20]
	train_indices = [num for num in range(25) if num not in test_indices]

	X_train, X_test = X[train_indices], X[test_indices]
	y_train, y_test = y[train_indices], y[test_indices]
	label_train, label_test = label[train_indices], label[test_indices]

	X_train_mat = vec.fit_transform(X_train).toarray()
	X_test_mat = vec.transform(X_test).toarray()
	pickle.dump(vec, open("vectorizer.pkl", "wb"))
	
	return X_train_mat, X_test_mat, y_train, y_test

def fit_model(X_train_mat, y_train):
	rf = RandomForestRegressor() 
	rf.fit(X_train_mat, y_train)
	return rf

def predict_model(model, X_test_mat):
	return model.predict(X_test_mat)

if __name__ == '__main__':
	data = read_data()
	X_train_mat, X_test_mat, y_train, y_test = get_features(data)
	model = fit_model(X_train_mat, y_train)
	predictions = predict_model(model, X_test_mat)
	pickle.dump(model, open("model.pkl", "wb"))
	print "Predictions for your articles are", predictions
	print "R-squared for model is", model.score(X_test_mat, y_test)


