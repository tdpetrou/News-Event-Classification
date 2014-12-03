import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time
import sys
import unicodedata
from time import mktime
from datetime import datetime, timedelta

class msnbc_scrape():
	def __init__(self, day):
		'''
		Initialize base link
		'''
		self.day = day

		today = datetime.now()
		DD = timedelta(days=self.day)
		self.earliest_date = (today - DD).strftime('%Y-%m-%d')
	
	def initialize(self):
		self.links = []
		self.pub_dates = []
		self.titles = []
		self.image_urls = []
		self.descriptions = []

	def get_links(self):
		'''
		return links with missing www.msnbc.com attached
		'''
		for i in range(4):
			if (i + 1) % 50 == 0:
				print "article page link", i
				time.sleep(30)
			req = requests.get(self.base + str(i) + '&f[0]=bundle%3Aarticle')
			#print self.base + str(i) + '&f[0]=bundle%3Aarticle'
			soup = BeautifulSoup(req.text)
			#msnbc does not return the base link. must add it here
			self.links.extend(['http://www.msnbc.com' + a['href'] for a in soup.findAll('a', {'class': 'search-result__teaser__title__link'})])
		self.links = [ item for pos,item in enumerate(self.links) if self.links.index(item)==pos ]

	def get_articles(self):
		'''
		return articles
		'''
		articles = []
		final_links = []
		for i, link in enumerate(self.links):
			if (i + 1) % 50 == 0:
				print "article scraped",i
				time.sleep(3)
			try:
				req = requests.get(link)
			except:
				time.sleep(3)
			if req.status_code == 200:
				soup = BeautifulSoup(req.text)
				pubdate = soup.findAll('div',  {'class' : "field field-name-field-publish-date field-type-datestamp field-label-hidden"})[0].find('time').text
				pubdate = time.strptime(pubdate[:8], '%m/%d/%y')
				pubdate = datetime.fromtimestamp(mktime(pubdate))
				pubdate = pubdate.strftime('%Y-%m-%d')
				if pubdate < self.earliest_date:
					print "toooooooooo early"
					print pubdate
					break
				self.pub_dates.append(pubdate)
				try:
					text = soup.findAll('div', {'class':'field field-name-body field-type-text-with-summary field-label-hidden'})[0].text
				except IndexError:
					continue
				text = self.decode_unicode(text)
		
				try:
					title  = soup.findAll(attrs = {'class' : "is-title-pane panel-pane pane-node-title"})[0].text
				except IndexError:
					self.titles.append('None')
				self.titles.append(self.decode_unicode(title))
				#get image urls and descriptions
				try:
					self.image_urls.append(soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content'])
				except IndexError:
					self.image_urls.append('#')
				try:
					desc = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
					self.descriptions.append(self.decode_unicode(desc))					
				except IndexError:
					self.descriptions.append('None')
				
				articles.append(text)
				final_links.append(link)
			else:
				print "sleeping"
				time.sleep(2)

		self.links =  final_links
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
		print "\n\n\n\nMSNBC"
		self.initialize()
		self.search_term = search_term
		self.base = 'http://www.msnbc.com/search/"' + search_term + '"?sm_field_issues=&sm_field_show=&date[min]&date[max]&date[date_selector]=&page='
		self.get_links()
		print "num links is", len(self.links)

		articles = self.get_articles()
		frame = pd.DataFrame({'text' : articles, 'url' : self.links, 'source' : 'MSNBC', \
			'publish_date': self.pub_dates, 'category' : self.search_term, 'title' : self.titles, \
			'image_url'  : self.image_urls, 'description' : self.descriptions}, \
			columns = ['source', 'url', 'image_url', 'title', 'description', 'text', 'publish_date', 'category'])
		frame.to_csv('data/msnbc_' + self.search_term.replace(' ', '_') + '_data.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
	search_term = sys.argv[1]
	msnbc = msnbc_scrape(10)
	msnbc.run(search_term)
