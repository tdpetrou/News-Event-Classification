import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def read_major_category():
	major_df = pd.read_csv('data/' + major_category + '_subtopics.csv' )
	sub_df = major_df[major_df['subcategory'] == subcategory]
	sub_df = sub_df.reset_index(drop=True)
	return sub_df

def make_key_words():
	with open('data/all_stops_stemmed.txt', 'r') as f:
		stop_stemmed = [line for line in f]

	sub_cat_vec = TfidfVectorizer(stop_words=stop_stemmed, max_features=200) #specific just to sub-catgeroy
	X_sub_cat = sub_cat_vec.fit_transform(sub_df['text_stemmed']).toarray()
	all_words = np.array(sub_cat_vec.get_feature_names())
	key_words_df = pd.DataFrame({'word': all_words, 'score' : 0}, columns=['word', 'score'])
	key_words_df.to_csv('data/key_words_' + major_category + '_' + subcategory.replace(' ', '_') + '.csv', index=False)


if __name__ == '__main__':
	major_category = sys.argv[1]
	subcategory = sys.argv[2]
	sub_df = read_major_category()
	make_key_words()