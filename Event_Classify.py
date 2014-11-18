import sys
sys.path.insert(0, 'scrapers')

from fox_scrape import fox_scrape
from msnbc_scrape import msnbc_scrape
from npr_scrape import npr_scrape
from nyt_scrape import nyt_scrape

from clean_scraped_data import clean_data
from classify_and_score_articles import classify_document
from get_event_score_ranges import Event_Score_Range
import pandas as pd



class Event_Classify():

	def __init__(self):
		self.topic_list = ['abortion', 'affordable care act', 'gay', 'gun', 'immigration', \
			'marijuana', 'obamacare', 'palestine', 'terrorism']
			#palestine not showing up much
		#self.topic_list = ['palestine']

	def run_scrapers(self, days=14):

		fox = fox_scrape(days)
		msnbc = msnbc_scrape(days)
		npr = npr_scrape(days)
		nyt = nyt_scrape(days)

		for topic in self.topic_list:
			print "\n\n", topic, "\n\n"
			fox.run(topic)
			msnbc.run(topic)
			npr.run(topic)
			nyt.run(topic)

	def clean_data(self):
		clean = clean_data()
		for topic in self.topic_list:
			clean.run(topic)

	def combine_data(self):
		a = pd.read_csv('data/combined_affordable_care_act.csv')
		o = pd.read_csv('data/combined_obamacare.csv')
		aca = pd.concat([a,o])
		aca = aca.drop_duplicates()
		aca.to_csv('data/combined_aca.csv', index=False)

	#explore topics separately 

	def get_event_score_range(self): 
		'''
		A csv is created that has the max and min scores for each of the suptopics
		This method should only be run once or perhaps again if there is lots of new data, a new model
		or a new scoring system
		'''
		event = Event_Score_Range()
		event.store_scores()

	def attach_and_rank_topics(self):
		self.topic_list = ['abortion', 'aca', 'gay', 'gun', 'immigration', \
			'marijuana', 'palestine', 'terrorism']
		for topic in self.topic_list:
			classify = classify_document(topic)
			classify.run()


if __name__ == '__main__':
	EC = Event_Classify()
	# EC.run_scrapers()
	# EC.clean_data()
	EC.combine_data()
	EC.attach_and_rank_topics()

