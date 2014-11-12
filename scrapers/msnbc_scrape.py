import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time
import sys

class msnbc_scrape():
	def __init__(self, search_term):
		'''
		Initialize base link
		'''
		self.search_term = search_term
		self.base = 'http://www.msnbc.com/search/"' + search_term + '"?sm_field_issues=&sm_field_show=&date[min]&date[max]&date[date_selector]=&page='
		self.links = []
		self.pub_dates = []
		self.titles = []

	def get_links(self, base):
		'''
		return links with missing www.msnbc.com attached
		'''
		for i in range(50):
			if (i + 1) % 50 == 0:
				print "article page link", i
				time.sleep(30)
			req = requests.get(self.base + str(i) + '&f[0]=bundle%3Aarticle')
			soup = BeautifulSoup(req.text)
			#msnbc does not return the base link. must add it here
			self.links.extend(['http://www.msnbc.com' + a['href'] for a in soup.findAll('a', {'class': 'search-result__teaser__title__link'})])
		self.links =  list(set(self.links))

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
				print req.url
			except:
				time.sleep(3)
			if req.status_code == 200:
				soup = BeautifulSoup(req.text)
				try:
					text = soup.findAll('div', {'class':'field field-name-body field-type-text-with-summary field-label-hidden'})[0].text
				except IndexError:
					print link
					continue
				text = str(re.sub('[^\w\s]+', ' ',text))
				text = str(re.sub('[\n]+', ' ',text))
				self.pub_dates.append(soup.findAll('div',  {'class' : "field field-name-field-publish-date field-type-datestamp field-label-hidden"})[0].find('time').text)
				try:
					self.titles.append(str(re.sub('[^\w\s]+', ' ',soup.findAll(attrs = {'class' : "is-title-pane panel-pane pane-node-title"})[0].text)))
				except IndexError:
					self.titles.append('None')
				articles.append(text)
				final_links.append(link)
			else:
				print "sleeping"
				time.sleep(2)

		self.links =  final_links
		return articles

if __name__ == '__main__':
	msnbc = msnbc_scrape(sys.argv[1])
	msnbc.get_links(msnbc.base)
	print "num links is", len(msnbc.links)
	articles = msnbc.get_articles()
	frame = pd.DataFrame({'text' : articles, 'url' : msnbc.links, 'source' : 'MSNBC', \
		'publish_date': msnbc.pub_dates, 'category' : msnbc.search_term, 'title' : msnbc.titles}, \
		columns = ['source', 'url', 'title', 'text', 'publish_date', 'category'])
	frame.to_csv('data/msnbc_' + msnbc.search_term.replace(' ', '_') + '_data.csv', index=False)