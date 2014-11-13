#attach event score
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
import pickle, sys

def get_event_score():

	#vec = pickle.load(open("pickles/vec_" + category + ".pkl", "rb"))
	sub_cat_df = pd.read_csv('data/combined_' + category + '_subtopics.csv')
	sub_cat_df = sub_cat_df[sub_cat_df['subcategory'] == 'Drug Cartels']
	sub_cat_df = sub_cat_df.reset_index(drop=True)
	vec = pickle.load(open("pickles/vec_marijuana_drug_cartels.pkl", "rb"))
	X_sub_cat = vec.fit_transform(sub_cat_df['text_stemmed']).toarray()
	sub_cat_sort = np.argsort(-X_sub_cat, axis = 1)
	all_words = np.array(vec.get_feature_names())
	top_words = all_words[sub_cat_sort[:,:20]]

	key_words = pd.read_csv('data/key_words/key_words_marijuana_drug_cartels_final.csv')
	event_word_dict =  dict(zip(key_words['word'].values, key_words['score'].values))

	event_scores = []
	for line in top_words:
	    event_score = 0
	    for word in line:
	        event_score += event_word_dict.get(word, 0)
	    event_scores.append(event_score)
	sub_cat_df['event score'] = event_scores
	sub_cat_df.to_csv('data/' + category + '_Drug_Cartels_' + 'Event_Score.csv', index=False)

if __name__ == '__main__':
	category = sys.argv[1] #loop through to get subcats
	get_event_score()