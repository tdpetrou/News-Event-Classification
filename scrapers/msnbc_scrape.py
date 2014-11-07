import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time
import sys

def get_links(base):
	links = []
	for i in range(3):
		req = requests.get(base + str(i) + '&f[0]=bundle%3Aarticle')
		soup = BeautifulSoup(req.text)
		#msnbc does not return the base link. must add it here
		links.extend(['http://www.msnbc.com' + a['href'] for a in soup.findAll('a', {'class': 'search-result__teaser__title__link'})]) # if a['href'][:6] == '/msnbc'])
	return list(set(links))

def get_articles(links):
	articles = []
	pub_dates = []
	final_links = []
	for link in links:
		req = requests.get(link)
		if req.status_code == 200:
			soup = BeautifulSoup(req.text)
			try:
				text = soup.findAll('div', {'class':'field field-name-body field-type-text-with-summary field-label-hidden'})[0].text
			except IndexError: #some links return videos or polls that have no article
				print link
				continue
			text = str(re.sub('[^\w\s]+', ' ',text))
			text = str(re.sub('[\n]+', ' ',text))
			pub_dates.append(soup.findAll('div',  {'class' : "field field-name-field-publish-date field-type-datestamp field-label-hidden"})[0].find('time').text)
			articles.append(text)
			final_links.append(link)
		else:
			print "sleeping"
			time.sleep(2)

	return final_links, articles, pub_dates

if __name__ == '__main__':
	search_term = sys.argv[1]
	base = 'http://www.msnbc.com/search/' + search_term + '?sm_field_issues=&sm_field_show=&date[min]&date[max]&date[date_selector]=&page='
	links = get_links(base)
	print "num links is", len(links)
	links, articles, pub_dates = get_articles(links)
	frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'MSNBC', 'publish_date': pub_dates, 'category' : search_term}, \
		columns = ['source', 'url', 'text', 'publish_date', 'category'])
	frame.to_csv('data/msnbc_' + search_term + '_data.csv', index=False)