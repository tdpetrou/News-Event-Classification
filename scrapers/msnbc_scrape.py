import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time
import sys
import datetime

class msnbc_scrape():
	def __init__(self, day):
		'''
		Initialize base link
		'''
		self.day = day

		today = datetime.datetime.now()
		DD = datetime.timedelta(days=self.day)
		self.earliest_date = (today - DD).strftime('%m/%d/%y')
	
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
				if pubdate < self.earliest_date:
					print "toooooooooo early"
					print pubdate
					break
				self.pub_dates.append(pubdate)
				try:
					text = soup.findAll('div', {'class':'field field-name-body field-type-text-with-summary field-label-hidden'})[0].text
				except IndexError:
					continue
				text = str(re.sub('[^\w\s]+', ' ',text))
				text = str(re.sub('[\n]+', ' ',text))
		
				try:
					self.titles.append(str(re.sub('[^\w\s]+', ' ',soup.findAll(attrs = {'class' : "is-title-pane panel-pane pane-node-title"})[0].text)))
				except IndexError:
					self.titles.append('None')

				#get image urls and descriptions
				try:
					self.image_urls.append(soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content'])
				except IndexError:
					self.image_urls.append('#')
				try:
					desc = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
					# print 'desc', desc
					self.descriptions.append(str(re.sub('[^\w\s]+', ' ', desc)))
				except IndexError:
					self.descriptions.append('None')
				articles.append(text)
				final_links.append(link)
			else:
				print "sleeping"
				time.sleep(2)

		self.links =  final_links
		return articles

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
		frame.to_csv('data/msnbc_' + self.search_term.replace(' ', '_') + '_data.csv', index=False)

if __name__ == '__main__':
	pass
