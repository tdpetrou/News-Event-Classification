import requests
import re
import pandas as pd
from dateutil import parser
import time
import sys
import datetime

class npr_scrape():

	def __init__(self, day):
		'''
		Initialize api keys and base url for NPR API query
		'''
		self.api_key = 'MDE3MzEyOTEwMDE0MTUxMjU4MjczNTcwMw001'
		self.base_url = 'http://api.npr.org/query'
		self.day = day

	def initialize(self):
		self.links = []
		self.pub_dates = []
		self.titles = []
		self.image_urls = []
		self.descriptions = []

	def get_articles(self):
		'''
		Get all articles with given search word taken from system argument
		returns text of articles
		'''
		all_articles = []
		today = datetime.datetime.now()
		DD = datetime.timedelta(days=self.day)
		
		endDate = today.strftime('%Y%m%d')
		startDate = (today - DD).strftime('%Y%m%d')
		pub_date = endDate
		art_num = 1
		start_num = 1
		while pub_date > startDate:
			params = {'apiKey' : self.api_key, 'output': 'JSON', 'endDate' : endDate, \
				'searchTerm' : self.search_word, 'startNum' : start_num, 'requiredAssets' : 'text'}

			req = requests.get(self.base_url, params=params)
			if req.status_code == 200:
				j = req.json()
				if not j.has_key('list'):  #check for keys. Some articles don't have these
					continue
				if not j['list'].has_key('story'):
					continue
				for story in j['list']['story']: 
					try:
						text = ' '.join([par['$text'] for par in story['text']['paragraph']])
						pub_date = parser.parse(story['pubDate']['$text']).strftime("%Y%m%d")
					except KeyError:
						text = ''
						if not story['text'].has_key('paragraph'):
							continue
						for par in story['text']['paragraph']:
							text += par.get('$text', ' ')
						pub_date = parser.parse(story['pubDate']['$text']).strftime("%Y%m%d")
					if pub_date < startDate:
						break
					if len(text) < 500:
						continue
					art_num += 1
					if art_num % 50 == 0:
						print "article scraped", art_num, endDate, startDate
					try:
						self.image_urls.append(story['image'][0]['src'])
					except:
						self.image_urls.append('#')
					try:
						desc = story['teaser']['$text']
						self.descriptions.append(str(re.sub('[^\w\s]+', ' ', desc)))
					except:
						self.descriptions.append('none')
					all_articles.append(str(re.sub('[^\w\s]+', ' ', text)))
					self.links.append(story['link'][0]['$text'])
					self.pub_dates.append(pub_date)
					self.titles.append(str(re.sub('[^\w\s]+', ' ', story['title']['$text'])))
				start_num += 10
				if start_num > 300:
					start_num = 1
					endDate = min(self.pub_dates)
					
			else:
				print "Sleepy..."
				# account for rate limiting
				time.sleep(2)

		return all_articles

	def run(self, search_word):
		print "\n\n\n\nNPR"
		self.initialize()
		self.search_word = search_word
		articles = self.get_articles()
		frame = pd.DataFrame({'text' : articles, 'url' : self.links, 'source' : 'NPR', 'publish_date': self.pub_dates, \
			'category' : self.search_word, 'title' : self.titles, 'image_url' : self.image_urls, 'description': self.descriptions}, \
			columns = ['source', 'url', 'image_url', 'title', 'description', 'text', 'publish_date', 'category'])
		frame.to_csv('data/npr_' + self.search_word.replace(' ', '_') + '_data.csv', index=False)	

if __name__ == '__main__':
	pass

