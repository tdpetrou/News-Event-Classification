import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
import pickle

def read_data():
	'''
	reads data from csv that I generated from copying and pasting articles from
	5 different news sources
	'''
	wiki = pd.read_csv("wikipedia_data.csv")
	fox = pd.read_csv("fox_data.csv")
	npr = pd.read_csv("npr_data.csv")
	cnn = pd.read_csv("cnn_data.csv")
	cnn = cnn[cnn['text'].apply(str) != 'nan']
	data = pd.concat((wiki[['source', 'text', 'rating']], fox[['source', 'text', 'rating']], 
		npr[['source', 'text', 'rating']], cnn[['source', 'text', 'rating']] ), ignore_index=True)
	return data

def get_features(data):
	vec = TfidfVectorizer(stop_words='english', max_features = 1000)
	X = data['text'].values
	y = data['rating']


	X_train, X_test, y_train, y_test = train_test_split(X, y)

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


