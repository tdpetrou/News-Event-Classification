import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import time
import sys
from dateutil import parser
import time
import datetime
import unicodedata


class fox_scrape():
	def __init__(self, day):
		self.day = day

	def initialize(self):
		self.pub_dates = []
		self.links = []
		self.titles = []
		self.image_urls = []
		self.descriptions = []

	def create_base(self, start_date, end_date, search_term):
		base = 'http://www.foxnews.com/search-results/search?&sort=date&q="' + search_term + \
				'"&ss=fn&mediatype=Text&daterange=' + \
					start_date + '%2C' + end_date + '&start='
		return base

	def get_links(self):
		today = datetime.datetime.now()
		DD = datetime.timedelta(days=self.day) #date difference

		start_date = (today - DD).strftime('%Y-%m-%d') #make this one month before end_date. This is just the initial date difference date
		end_date = time.strftime("%Y-%m-%d") #todays date
		earliest_date = (today - DD).strftime('%Y-%m-%d') #this is the very earliest that you want to search back till
		date_diff = parser.parse(end_date) - parser.parse(start_date)
		base = self.create_base(start_date, end_date, self.search_term)
		links = []
		total_links = 0
		while start_date >= earliest_date and total_links < 500:
			new_links =['temp']
			i = 0
			while new_links:
				req = requests.get(base + str(i * 10))
				soup = BeautifulSoup(req.text, 'html.parser')
				new_links = [a['href'] for a in soup.findAll('a', {'class' : 'ez-title'})]
				links.extend(new_links)
				i += 1
				total_links += len(new_links)
				print "total links", total_links
			start_date = (parser.parse(start_date) - date_diff).strftime("%Y-%m-%d")
			end_date = (parser.parse(end_date) - date_diff).strftime("%Y-%m-%d")
			base = self.create_base(start_date, end_date, self.search_term)
			print "new dates ", start_date, end_date
		self.links =  list(set(links))
		#self.links = [link for link in self.links if 'latino.foxnews' not in link]

	def get_articles(self):
		articles = []
		pub_dates = []
		final_links = []
		titles = []
		image_urls = []
		descriptions = []
		
		print "length of links", len(self.links)
		for i, link in enumerate(self.links):
			if (i + 1) % 50 == 0:
				print "article scraped", i
				time.sleep(30)
			req = requests.get(link)
			if req.status_code == 200:
				soup = BeautifulSoup(req.text)
				try:
					text = ' '.join([par.text for par in soup.findAll('div', {'itemprop': 'articleBody'})[0].findAll('p')])
				except IndexError:
					continue
				text = self.decode_unicode(text)
				text = text.replace('ADVERTISEMENT', ' ')
				articles.append(text)
				dt = soup.findAll('time')[0]['datetime']
				self.pub_dates.append(dt[:10])
				try:
					self.image_urls.append(soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content'])
				except IndexError:
					self.image_urls.append('#')
				try:
					desc = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
					desc = self.decode_unicode(desc)
					self.descriptions.append(desc)
				except IndexError:
					self.descriptions.append('None')
				final_links.append(link)
				self.titles.append(self.decode_unicode(soup.findAll('meta', {'name' : 'dc.title'})[0]['content']))
			else:
				print "sleeping"
				time.sleep(5)
		self.links = final_links
		return articles

	def decode_unicode(self, text):
		text = unicode(text)
		a = '/'; b = '\''
		text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
		text = str(re.sub('[\n]+', ' ', text))
		text = text.replace(a, '')
		text = text.replace(b, '')
		return text

	def run(self, search_term):
		print "\n\n\n\nFox news"
		self.initialize()
		self.search_term = search_term
		file_search_term =  'data/fox_' + self.search_term.replace(' ', '_') + '_data.csv'
		self.get_links()

		#use a limited number of links since fox is slow
		self.links = self.links[:300]

		articles = self.get_articles()
		frame = pd.DataFrame({'text' : articles, 'url' : self.links, 'source' : 'Fox', \
			'publish_date' : self.pub_dates, 'category' : self.search_term, 'title' : self.titles, \
			'image_url' : self.image_urls, 'description' : self.descriptions}, \
				 columns = ['source', 'url', 'image_url', 'title', 'description', 'text', 'publish_date', 'category'])	
		frame.to_csv(file_search_term, index=False, encoding='utf-8')

if __name__ == '__main__':
	search_term = sys.argv[1]
	fox = fox_scrape(1)
	fox.run(search_term)

