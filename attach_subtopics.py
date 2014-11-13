#attach subtopics
import pandas as pd
import numpy as np
import sys, pickle

def add_subtopics():
	df_major = pd.read_csv('data/combined_' + category + '.csv')
	with open('data/subtopics/' + category + '_subtopics.txt') as f:
		topics = [line[:-1] for line in f]
	nmf_matrix = pickle.load( open( "pickles/nmf_matrix_" + category + ".pkl", "rb" ) )
	doc_topics_frame = pd.DataFrame(nmf_matrix)
	df_major['subcategory'] = doc_topics_frame.apply(lambda x: topics[np.argmax(x)], axis=1)
	df_major.to_csv('data/combined_' + category + '_subtopics.csv', index=False)
	
if __name__ == '__main__':
	category = sys.argv[1]
	add_subtopics()