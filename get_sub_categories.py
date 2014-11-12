from sklearn.decomposition import NMF
from nltk.corpus import stopwords
import seaborn
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer


class sub_categories():
	def __init__(self):
		pass

	def stem_and_vectorize(self, sents, category, stem=False):
		current_df = sents[sents['category'] == category]
		current_df = current_df.reset_index(drop=True)
		snowball = SnowballStemmer('english')

		with open('data/all_stops.txt', 'r') as f:
			stop = [line for line in f]

		if stem:
			stop = [snowball.stem(word) for  word in stop]
			vec = TfidfVectorizer(stop_words=stop, max_features=2000)
			X = vec.fit_transform(current_df['text_stemmed'].values)	
		else:
			vec = TfidfVectorizer(stop_words=stop, max_features=2000)
			X = vec.fit_transform(current_df['text'].values)
		return X, vec

	def add_subcategories(self, X, vec, df, topics, num_topics):
		nmf = NMF(n_components=num_topics, random_state=1)
		doc_topics = pd.DataFrame(nmf.fit_transform(X))
		model = nmf.fit(X)
		df['subcategory'] = ''
		df['subcategory'] = doc_topics.apply(lambda x: topics[np.argmax(x)], axis=1)
		return nmf, df
		

	def print_graph(self, model, topics, vec, num_topics, main_topic):	
		fig = plt.figure(figsize = (12,10))
		n_top_words = 10
		plt.figure(figsize=(10,18))
		feature_names = vec.get_feature_names()
		for topic_idx, topic in enumerate(model.components_):
		    print("Topic #%d:" % (topic_idx + 1))
		    top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
		    print top_words
		    plt.subplot(num_topics, 2, topic_idx + 1)
		    plt.barh(range(10), sorted(topic)[-n_top_words:])
		    plt.yticks(range(10), top_words)
		    plt.title(topics[topic_idx])
		    print()
		plt.tight_layout()
		plt.savefig('graphs/' + main_topic + '.png')

	def main(self):
		sents = pd.read_csv('data/combined_data.csv')
		abortion = sents[sents['category'] == 'abortion']
		marijuana = sents[sents['category'] == 'marijuana']
		abortion = abortion.reset_index(drop=True)
		marijuana = marijuana.reset_index(drop=True)

		#X_abortion, vec_abortion = self.stem_and_vectorize(abortion, 'abortion')
		X_marijuana, vec_marijuana = self.stem_and_vectorize(marijuana, 'marijuana')

		#abortion_topics = np.array(['Abortion Clinics', 'Religious Opinion on Abortion', 'Campaigning'])
		marijuana_topics = np.array(['Drugs and Kids', 'Medical Legalization', 'Drug Cartels', 'Campaigning', 'Court Cases', 'Drugs in Sports'])
		
		#nmf_abortion, abortion = self.add_subcategories(X_abortion, vec_abortion, abortion, abortion_topics, 3)
		nmf_marijuana, marijuana = self.add_subcategories(X_marijuana, vec_marijuana, marijuana, marijuana_topics, 6)

		marijuana.to_csv('data/marijuana_subtopics.csv', index=False)
		

		#self.print_graph(nmf_abortion, abortion_topics, vec_abortion, 3, 'Abortion')
		self.print_graph(nmf_marijuana, marijuana_topics, vec_marijuana, 6, 'Marijuana')

	
if __name__ == '__main__':
	sub_category = sub_categories()
	sub_category.main()
	