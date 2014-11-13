#attach subtopics
import pandas as pd
import numpy as np
import sys, pickle
import matplotlib.pyplot as plt
import seaborn

def add_subtopics():
	df_major = pd.read_csv('data/combined_' + category + '.csv')
	with open('data/subtopics/' + category + '_subtopics.txt') as f:
		topics = [line[:-1] for line in f]
	nmf_matrix = pickle.load( open( "pickles/nmf_matrix_" + category + ".pkl", "rb" ) )
	doc_topics_frame = pd.DataFrame(nmf_matrix)
	df_major['subcategory'] = doc_topics_frame.apply(lambda x: topics[np.argmax(x)], axis=1)
	df_major.to_csv('data/combined_' + category + '_subtopics.csv', index=False)


	nmf = pickle.load(open("pickles/nmf_" + category + ".pkl", "rb"))
	vec = pickle.load(open("pickles/vec_" + category + ".pkl", "rb"))

	num_topics = len(topics)
	feature_names = vec.get_feature_names()
	fig = plt.figure(figsize = (10,24))
	n_top_words = 15
	for topic_idx, topic in enumerate(nmf.components_):
	    top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
	    plt.subplot(num_topics, 2, topic_idx + 1)
	    plt.barh(range(n_top_words), sorted(topic)[-n_top_words:])
	    plt.yticks(np.linspace(.5, n_top_words + .5, n_top_words + 1), top_words)
	    plt.title(topics[topic_idx]);
	plt.tight_layout()
	plt.savefig('graphs/final_' + category + '.png')
	
if __name__ == '__main__':
	category = sys.argv[1].replace(' ','_')
	add_subtopics()