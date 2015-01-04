'''
This script is used to explore possible subtopics of the articles by major category.
Two parameters are passed, the first being the major category and the second the estimated
number of subtopics. Returned is a plot that has the estimated number of subtopics each plotted
with the top 15 words. From here, the user would examine the plots by hand to determine an
appropriate name for the subtopic. This is an iterative process that could take running the
script multiple times to get an sensible number of subtopics that make sense to a human.
Also, the TfidfVectorizer and the nmf model are pickled to be used on new articles to quickly
classify them.
'''

from sklearn.decomposition import NMF
import seaborn
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import sys, pickle

def create_nmf():
	df_major = pd.read_csv('data/combined_' + category + '.csv')

	with open('data/all_stops.txt', 'r') as f:
		stop_words = [line[:-1] for line in f]

	stop_words.extend(['npr', 'one', 'two', 'new', 'fox', 'times', 'las', 'se', 'por', 'un', \
		'del', 'en', 'al', 'con', 'son', 'sin', 'nbc' ,'npr', 'msnbc', 'york'])

	vec = TfidfVectorizer(stop_words=stop_words, max_features=2000)
	X = vec.fit_transform(df_major['text'].values)

	nmf = NMF(n_components=num_topics, random_state=1)
	nmf_matrix = nmf.fit_transform(X)

	pickle.dump(nmf, open("pickles/nmf_" + category + ".pkl", "wb"))
	pickle.dump(nmf_matrix, open("pickles/nmf_matrix_" + category + ".pkl", "wb"))
	pickle.dump(vec, open("pickles/vec_" + category + ".pkl", "wb"))

	feature_names = vec.get_feature_names()
	fig = plt.figure(figsize = (10,18))
	n_top_words = 15
	for topic_idx, topic in enumerate(nmf.components_):
	    top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
	    plt.subplot(num_topics, 2, topic_idx + 1)
	    plt.barh(range(n_top_words), sorted(topic)[-n_top_words:])
	    plt.yticks(np.linspace(.5, n_top_words + .5, n_top_words + 1), top_words)
	    plt.title(topic_idx + 1);
	plt.tight_layout()
	plt.savefig('data/explore_topics_nmf/explore_' + category + '.png')

if __name__ == '__main__':
	category = sys.argv[1].replace(' ', '_')
	num_topics = int(sys.argv[2])
	nmf = create_nmf()
