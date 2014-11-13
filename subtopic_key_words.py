import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle


def read_major_category():
	major_df = pd.read_csv('data/combined_' + major_category + '_subtopics.csv' )
	all_sub_cats = np.unique(major_df['subcategory'])
	for sub_cat in all_sub_cats:
		sub_df = major_df[major_df['subcategory'] == sub_cat]
		sub_df = sub_df.reset_index(drop=True)
		make_key_words(sub_df, sub_cat)

def make_key_words(sub_df, sub_cat):
	sub_cat_vec = TfidfVectorizer(stop_words=stop_stemmed, max_features=300) #specific just to sub-catgeroy
	X_sub_cat = sub_cat_vec.fit_transform(sub_df['text_stemmed']).toarray()
	all_words = np.array(sub_cat_vec.get_feature_names())
	key_words_df = pd.DataFrame({'word': all_words, 'score' : 0}, columns=['word', 'score'])
	key_words_df.to_csv('data/key_words/key_words_' + major_category + '_' + sub_cat.replace(' ', '_') + '.csv', index=False)
	pickle.dump(sub_cat_vec, open("pickles/vec_" + major_category + '_' + sub_cat.replace(' ', '_') + ".pkl", "wb"))


if __name__ == '__main__':
	major_category = sys.argv[1]
	with open('data/all_stops_stemmed.txt', 'r') as f:
		stop_stemmed = [line[:-1] for line in f]
	read_major_category()