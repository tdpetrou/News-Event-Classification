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

	def stem_and_vectorize(self, sents, num_topics, category, stem=False):
		snowball = SnowballStemmer('english')
		stop = stopwords.words('english') 
		extra_sw = ['new', 'mr', 'said', 'one', 'like', 'ms', 'would', 'use', 'people', 'say', 
		            'says', 'thing', 'want', 'go', 'know', 'get', 'hes', 'because', 'going', 'its'
		            , 'think', 'that', 'dont', 'im', 'make', 'way', 'time', 'thats', 'got', 'really', 'lot', 'see', 'many']
		stop.extend(extra_sw)
		if stem:
			stop = [snowball.stem(word) for  word in stop]
			vec = TfidfVectorizer(stop_words=stop, max_features=2000)
			X = vec.fit_transform(sents[sents['category'] == category]['text_stemmed'].values)	
		else:
			vec = TfidfVectorizer(stop_words=stop, max_features=2000)
			X = vec.fit_transform(sents[sents['category'] == category]['text'].values)
		return X, vec

	def add_subcategories(self, X, vec, df, topics, num_topics):
		nmf = NMF(n_components=num_topics, random_state=1)
		doc_topics = pd.DataFrame(nmf.fit_transform(X))
		model = nmf.fit(X)
		df['subcategory'] = ''
		df['subcategory'] = doc_topics.apply(lambda x: topics[np.argmax(x)], axis=1)
		return nmf, df

	def combine_data(self, df, df2):
		combined_data = pd.concat([df, df2])
		combined_data.to_csv('data/combined_data_subcategory')

	def print_graph(self, model, topics, vec, num_topics):	
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
		plt.show()

	def main(self):
		sents = pd.read_csv('data/combined_data.csv')
		abortion = sents[sents['category'] == 'abortion']
		marijuana = sents[sents['category'] == 'marijuana']

		X_abortion, vec_abortion = self.stem_and_vectorize(abortion, 3, 'abortion')
		X_marijuana, vec_marijuana = self.stem_and_vectorize(marijuana, 5, 'marijuana')

		abortion_topics = np.array(['abortion clinics', 'religious opinion on abortion', 'campaign trail'])
		marijuana_topics = np.array(['marijuana legalization', 'domestic violence', 'mexican cartel', 'marijuana in sports', 'campaign trail']) 
		
		nmf_abortion, abortion = self.add_subcategories(X_abortion, vec_abortion, abortion, abortion_topics, 3)
		nmf_marijuana, marijuana = self.add_subcategories(X_marijuana, vec_marijuana, marijuana, marijuana_topics, 5)

		self.combine_data(abortion, marijuana)

		self.print_graph(nmf_abortion, abortion_topics, vec_abortion, 3)
		self.print_graph(nmf_marijuana, marijuana_topics, vec_marijuana, 5)

	
if __name__ == '__main__':
	sub_category = sub_categories()
	sub_category.main()
	