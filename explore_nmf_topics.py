#Explore the topics


from sklearn.decomposition import NMF
import seaborn
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
import sys, pickle

def create_nmf():
	df_major = pd.read_csv('data/combined_' + category + '.csv')
	# snowball = SnowballStemmer('english')

	with open('data/all_stops.txt', 'r') as f:
		stop_words = [line[:-1] for line in f]

	stop_words.extend(['npr', 'one', 'two', 'new', 'fox', 'york', 'times'])

	vec = TfidfVectorizer(stop_words=stop_words, max_features=2000)
	X = vec.fit_transform(df_major['text'].values)

	nmf = NMF(n_components=num_topics, random_state=1)
	#doc_topics = nmf.fit_transform(X)
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
