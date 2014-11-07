from __future__ import division
import pandas as pd
from nltk.stem import SnowballStemmer
import re

def get_sent_dict():
	sent = {}
	sent_stemmed = {}
	with open("data/sentiment.txt","r") as text:
		for line in text:
			key, value = line.split('\t')
			sent[key] = int(value)
			try:
				sent_stemmed[snowball.stem(key)] = int(value)
			except: #ascii error
				pass
	return sent, sent_stemmed

def score_sentiment(text, sent_dict):
	total_sent = 0
	words = text.split()
	for word in words:
		total_sent += sent_dict.get(word, 0)
	return total_sent / len(words)

def stem_text(text):
	return [snowball.stem(word) for word in re.sub(r'[^\w\s]','',text).lower().split()]

def join_data():
	nyt_m = pd.read_csv('data/nyt_marijuana_data.csv').drop_duplicates()
	nyt_a = pd.read_csv('data/nyt_abortion_data.csv').drop_duplicates()
	npr_m = pd.read_csv('data/npr_marijuana_data.csv').drop_duplicates()
	npr_a = pd.read_csv('data/npr_abortion_data.csv').drop_duplicates()
	fox_m = pd.read_csv('data/fox_marijuana_data.csv').drop_duplicates()
	fox_a =pd.read_csv('data/fox_abortion_data.csv').drop_duplicates()
	msnbc_m = pd.read_csv('data/msnbc_marijuana_data.csv').drop_duplicates()
	msnbc_a = pd.read_csv('data/msnbc_abortion_data.csv').drop_duplicates()

	combined_data = pd.concat([nyt_m, nyt_a, npr_a, npr_m, fox_m, fox_a, msnbc_a, msnbc_m])
	combined_data['text'] = combined_data['text'].astype(str)

	combined_data = combined_data[combined_data['text'].apply(len) > 500]
	return combined_data

def add_columns(data):
	data['num_words'] = data['text'].apply(lambda x: len(x.split()))
	data['sentiment'] = data['text'].apply(lambda x: score_sentiment(x, sent))

	data['text_stemmed'] = data['text'].apply(stem_text)
	data['sentiment_stemmed'] = data['text_stemmed'].apply(lambda x: score_sentiment(x, sent_dict))
	return data

if __name__ == '__main__':
	snowball = SnowballStemmer('english')
	sent, sent_stemmed = get_sent_dict()
	data = join_data()
	data = add_columns(data)
	data.to_csv('data/combined_data.csv', index=False)

