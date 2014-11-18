#attach event score
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
import pickle, sys

def get_event_score():

	#vec = pickle.load(open("pickles/vec_" + category + ".pkl", "rb"))
	with open('data/subtopics/' + category + '_subtopics.txt', 'r') as f:
		all_sub_cats = [line[:-1] for line in f]
	print all_sub_cats
	major_df = pd.read_csv('data/combined_' + category + '_subtopics.csv')

	for topic in all_sub_cats:
		topic_file = topic.replace(' ', '_') 
		sub_cat_df = major_df[major_df['subcategory'] == topic]
		sub_cat_df = sub_cat_df.reset_index(drop=True)

		key_words = pd.read_csv('data/key_words/final_key_words/key_words_' + category + '_' + topic_file + '_final.csv')
		event_word_dict =  dict(zip(key_words['word'].values, key_words['score'].values))

		event_scores = []
		tot_score = []
		for text in sub_cat_df['text_stemmed'].values:
		    event_score = 0
		    for word in text.split():
		        event_score += event_word_dict.get(word, 0)
		    l = len(text)
		    event_scores.append(event_score / float(l))
		    tot_score.append(event_score)
		sub_cat_df['event score'] = event_scores
		sub_cat_df['event score total'] = tot_score

		event_min = sub_cat_df['event score'].min()
		event_max = sub_cat_df['event score'].max()
		event_range = event_max - event_min
		sub_cat_df['event score scaled'] = (sub_cat_df['event score'] + event_min * -1) / event_range
		sub_cat_df.to_csv('data/event_scores/' + category + '_' + topic_file +  '_Event_Score.csv', index=False)

if __name__ == '__main__':
	category = sys.argv[1].replace(' ', '_') #loop through to get subcats
	get_event_score()