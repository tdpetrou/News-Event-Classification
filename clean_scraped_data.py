from __future__ import division
import pandas as pd
from nltk.stem import SnowballStemmer
import re, sys

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

def score_sentiment(text, sent_dict, total=False):
	total_sent = 0
	words = text.split()
	for word in words:
		total_sent += sent_dict.get(word, 0)
	if total:
		return total_sent
	return total_sent / len(words)

def stem_text(text):
	return ' '.join([snowball.stem(word) for word in re.sub(r'[^\w\s]',' ',text).lower().split()])

def join_data():
	nyt = pd.read_csv('data/nyt_' + major_category + '_data.csv').drop_duplicates()
	npr = pd.read_csv('data/npr_' + major_category + '_data.csv').drop_duplicates()
	fox = pd.read_csv('data/fox_' + major_category + '_data.csv').drop_duplicates()
	msnbc = pd.read_csv('data/msnbc_' + major_category + '_data.csv').drop_duplicates()

	combined_data = pd.concat([nyt, nyt, npr, npr])
	combined_data['text'] = combined_data['text'].astype(str)
	combined_data = combined_data[combined_data['text'].apply(len) > 500]
	# combined_data[(combined_data['category'] == 'obamacare') | (combined_data['category'] == 'affordable care act')]
	return combined_data

def add_columns(data):
	data['num_words'] = data['text'].apply(lambda x: len(x.split()))
	data['sentiment'] = data['text'].apply(lambda x: score_sentiment(x, sent))

	data['text_stemmed'] = data['text'].apply(stem_text)
	data['sentiment_stemmed'] = data['text_stemmed'].apply(lambda x: score_sentiment(x, sent_stemmed))

	data['sentiment_total']=data['text_stemmed'].apply(lambda x: score_sentiment(x, sent_stemmed, True))
	return data

if __name__ == '__main__':
	major_category = sys.argv[1]
	snowball = SnowballStemmer('english')
	sent, sent_stemmed = get_sent_dict()
	data = join_data()
	data = add_columns(data)
	data.to_csv('data/combined_' + major_category + '.csv', index=False)

