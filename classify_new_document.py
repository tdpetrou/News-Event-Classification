#classify new document
import pickle
import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class classify_document():

	def __init__(self, category):
		self.nmf = pickle.load(open("pickles/nmf_" + category + ".pkl", "rb"))
		self.vec = pickle.load(open("pickles/vec_" + category + ".pkl", "rb"))
		self.category = category

	def predict_category(self):
		with open('data/subtopics/' + self.category + '_subtopics.txt') as f:
		    topics = [line[:-1] for line in f]
		major_df = pd.read_csv('data/combined_' + self.category + '.csv')

		# rand = np.random.randint(0, len(major_df))
		text = major_df['text'].ix[rand]
		text_stemmed = major_df['text_stemmed'].ix[rand]
		X = self.vec.transform([text]).toarray()
		topic_id = np.argmax(self.nmf.transform(X), axis = 1)
		sub_topic = topics[topic_id[0]]
		major_df = pd.read_csv('data/event_scores/' + self.category + '_' + sub_topic.replace(' ', '_') + '_Event_Score.csv')
		sub_cat_df = major_df[major_df['subcategory'] == sub_topic]
		sub_cat_df = sub_cat_df.reset_index(drop=True)
		event_min = sub_cat_df['event score'].min()
		event_max = sub_cat_df['event score'].max()
		event_range = event_max - event_min
		
		sub_topic = sub_topic.replace(' ', '_')
		key_words = pd.read_csv('data/key_words/final_key_words/key_words_' + self.category + '_' + sub_topic + '_final.csv')
		event_word_dict =  dict(zip(key_words['word'].values, key_words['score'].values))

		event_score = 0
		for word in text_stemmed.split():
		    event_score += event_word_dict.get(word, 0)
		l = len(text)
		event_score = (event_score / float(l) + (-1 * event_min)) / event_range
		print sub_topic, event_score

if __name__ == '__main__':
	category = sys.argv[1].replace(' ', '_')
	classify = classify_document(category)
	classify.predict_category()