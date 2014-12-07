#classify new document
import pickle
import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class classify_document():

	def __init__(self, category):
		self.category = category
		self.category_replace = self.category.replace(' ', '_')

		self.nmf = pickle.load(open("pickles/nmf_" + self.category_replace + ".pkl", "rb"))
		self.vec = pickle.load(open("pickles/vec_" + self.category_replace + ".pkl", "rb"))
		self.subtopics = ''

	def predict_category(self):
		with open('data/subtopics/' + self.category + '_subtopics.txt') as f:
		    self.subtopics = np.array([line[:-1] for line in f])
		major_df = pd.read_csv('data/combined_' + self.category + '.csv')
		#There are some problems reading in the data that add random nulls. I remove them here
		# major_df = major_df[major_df['text'].isnull() == False]
		major_df['text'] = major_df['text'].astype(str)
		major_df['text_stemmed'] = major_df['text_stemmed'].astype(str)
		major_df = major_df[major_df['text'].apply(len) > 200]

		all_text = major_df['text'].values
		# all_text_stemmed = major_df['text_stemmed'].values

		print 'category ', self.category, ' all_text len', len(all_text)
		X = self.vec.transform(all_text).toarray()
		topic_id = np.argmax(self.nmf.transform(X), axis = 1)
		sub_topic = self.subtopics[topic_id]
		major_df['subcategory'] = sub_topic
		major_df.to_csv('data/combined_' + self.category + '_subtopics.csv', index=False)
		return major_df
		
	def add_event_scores(self, major_df):
		with open('data/subtopics/' + self.category + '_subtopics.txt') as f:
		    subtopics = np.array([line[:-1] for line in f])

		major_df = pd.read_csv('data/combined_' + self.category + '_subtopics.csv' )
		event_range_df = pd.read_csv('data/event_score_range.csv')

		for subtopic in subtopics:
		    sub_cat_df = major_df[major_df['subcategory'] == subtopic]
		    sub_cat_df = sub_cat_df.reset_index(drop=True)

		    specific_range_df =  event_range_df[(event_range_df['topic'] == self.category) & (event_range_df['subcategory'] == subtopic)]
		    event_min = specific_range_df['min'].min()
		    event_max = specific_range_df['max'].max()
		    event_range = event_max - event_min


		    subtopic = subtopic.replace(' ', '_')
		    key_words = pd.read_csv('data/key_words/final_key_words/key_words_' + self.category + '_' + subtopic + '_final.csv')
		    event_word_dict =  dict(zip(key_words['word'].values, key_words['score'].values))

		    all_stemmed = sub_cat_df['text_stemmed'].values
		    
		    event_score_total = []
		    event_scores = []
		    event_score_scaled = []
		    for text_stemmed in all_stemmed:
		        event_score = 0
		        for word in text_stemmed.split():
		            event_score += event_word_dict.get(word, 0)
		        event_score_total.append(event_score)
		        l = len(text_stemmed)
		        event_scores.append(event_score / float(l))
		        event_score = (event_score / float(l) + (-1 * event_min)) / event_range
		        event_score_scaled.append(event_score)
		    sub_cat_df['event score'] = event_scores
		    sub_cat_df['event score total'] = event_score_total
		    sub_cat_df['event score scaled'] = event_score_scaled
		    sub_cat_df.to_csv('data/event_scores/new/' + self.category + '_' + subtopic + '_event_scores.csv', index=False)
	def run(self):
		major_df = self.predict_category()
		self.add_event_scores(major_df)

if __name__ == '__main__':
	category = sys.argv[1].replace(' ', '_')
	classify = classify_document(category)
	major_df = classify.predict_category()
	classify.add_event_scores(major_df)