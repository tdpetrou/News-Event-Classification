from __future__ import division
import pandas as pd
from nltk.stem import SnowballStemmer
import re, sys

class clean_data():
	def __init__(self):
		pass

	def get_sent_dict(self):
		sent = {}
		sent_stemmed = {}
		with open("data/sentiment.txt","r") as text:
			for line in text:
				key, value = line.split('\t')
				sent[key] = int(value)
				try:
					sent_stemmed[self.snowball.stem(key)] = int(value)
				except: #ascii error
					pass
		return sent, sent_stemmed

	def score_sentiment(self, text, sent_dict, total=False):
		total_sent = 0
		words = text.split()
		for word in words:
			total_sent += sent_dict.get(word, 0)
		if total:
			return total_sent
		return total_sent / len(words)

	def stem_text(self, text):
		return ' '.join([self.snowball.stem(word) for word in re.sub(r'[^\w\s]',' ',text).lower().split()])

	def join_data(self):
		#add functionality to automatically detect all csv files
		nyt = pd.read_csv('data/nyt_' + self.major_category + '_data.csv').drop_duplicates()
		npr = pd.read_csv('data/npr_' + self.major_category + '_data.csv').drop_duplicates()
		fox = pd.read_csv('data/fox_' + self.major_category + '_data.csv').drop_duplicates()
		msnbc = pd.read_csv('data/msnbc_' + self.major_category + '_data.csv').drop_duplicates()

		combined_data = pd.concat([nyt, npr, fox, msnbc])
		combined_data['text'] = combined_data['text'].astype(str)
		combined_data = combined_data[combined_data['text'].apply(len) > 700]
		search_term = self.major_category.replace('_',' ')
		combined_data = combined_data[combined_data['text'].apply(lambda x: search_term in x.lower())]
		return combined_data

	def add_columns(self, data, sent, sent_stemmed):
		data['num_words'] = data['text'].apply(lambda x: len(x.split()))
		data['sentiment'] = data['text'].apply(lambda x: self.score_sentiment(x, sent))

		data['text_stemmed'] = data['text'].apply(self.stem_text)
		data['sentiment_stemmed'] = data['text_stemmed'].apply(lambda x: self.score_sentiment(x, sent_stemmed))

		data['sentiment_total']=data['text_stemmed'].apply(lambda x: self.score_sentiment(x, sent_stemmed, True))
		return data

	def run(self, category):
		self.major_category = category.replace(' ', '_')
		self.snowball = SnowballStemmer('english')
		sent, sent_stemmed = self.get_sent_dict()
		data = self.join_data()
		data = self.add_columns(data, sent, sent_stemmed)
		data.to_csv('data/combined_' + self.major_category + '.csv', index=False)


if __name__ == '__main__':
	pass


