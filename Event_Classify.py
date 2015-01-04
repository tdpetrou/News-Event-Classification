'''
This is the main file that is run nightly at 9 p.m. on the server by ways of a cron job.
This file scrapes, cleans, combines aca articles, finds the subtopics, attaches a score
to each article and writes this info to a mysql database online
'''
import sys
sys.path.insert(0, 'scrapers')

from fox_scrape import fox_scrape
from msnbc_scrape import msnbc_scrape
from npr_scrape import npr_scrape
from nyt_scrape import nyt_scrape
from bing_scrape import bing_scrape
from google_news_scrape import google_scrape

from clean_scraped_data import clean_data
from classify_and_score_articles import classify_document
from get_event_score_ranges import Event_Score_Range
from write_to_db import write_to_db
import pandas as pd


class Event_Classify():

	def __init__(self):
		'''
		These are the terms used in the search queries during web scraping or api interaction
		affordable care act and obamacare represent the same topic
		'''
		self.topic_list = ['abortion', 'affordable care act', 'gay', 'gun', 'immigration', \
			'marijuana', 'obamacare', 'palestine', 'terrorism']
		#self.topic_list = ['gun', 'immigration', 'marijuana', 'obamacare', 'palestine', 'terrorism']


	def run_scrapers(self, days=14):
		'''Scrape each news site. Days are the number of days to look back in time to find articles.
		The nightly scrapers only look back 1 day. Bing is not used because of the duplication to 
		google news.
		'''
		# bing = bing_scrape(days)
		google = google_scrape(days)
		fox = fox_scrape(days)
		msnbc = msnbc_scrape(days)
		npr = npr_scrape(days)
		nyt = nyt_scrape(days)

		for topic in self.topic_list:
			print "\n\n", topic, "\n\n"
			# bing.run(topic)
			google.run(topic)
			fox.run(topic)
			msnbc.run(topic)
			npr.run(topic)
			nyt.run(topic)

	def clean_data(self):
		'''Articles are cleaned. Many are discarded for being too short.'''
		clean = clean_data()
		for topic in self.topic_list:
			clean.run(topic)

	def combine_data(self):
		'''affordable care act and obamacare articles are combined into one file'''
		a = pd.read_csv('data/combined_affordable_care_act.csv')
		o = pd.read_csv('data/combined_obamacare.csv')
		aca = pd.concat([a,o])
		aca = aca.drop_duplicates()
		aca['category'] = 'aca'
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
		'''Each articles is classified into a subtopic. Based on this subtopic, it is evaluated to determine if a
		specific event has occurred given the domain specific dictionary
		'''
		self.topic_list = ['abortion', 'aca', 'gay', 'gun', 'immigration', \
			'marijuana', 'palestine', 'terrorism']
		for topic in self.topic_list:
			classify = classify_document(topic)
			classify.run()

	def write_db(self):
		'''writes article data to mysql database on bluehost server'''
		wdb = write_to_db()
		wdb.run()



if __name__ == '__main__':
	EC = Event_Classify()

	# EC.run_scrapers(1)
	# EC.clean_data()
	# EC.combine_data()
	EC.attach_and_rank_topics()
	EC.write_db()

