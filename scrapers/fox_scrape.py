import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import time
import sys
from dateutil import parser


def create_base(start_date, end_date, search_term):
	base = 'http://www.foxnews.com/search-results/search?&sort=date&q=' + search_term + \
			'&ss=fn&mediatype=Text&daterange=' + \
				start_date + '%2C' + end_date + '&start='
	return base

def get_links(search_term):
	start_date = "2014-10-01"
	end_date = "2014-11-01"
	earliest_date = "2009-01-01"
	date_diff = parser.parse(end_date) - parser.parse(start_date)
	base = create_base(start_date, end_date, search_term)
	links = []
	total_links = 0
	while start_date >= earliest_date and total_links < 3000:
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
		base = create_base(start_date, end_date, search_term)
		print "new dates ", start_date, end_date
	return list(set(links))

def get_articles(links):
	articles = []
	pub_dates = []
	final_links = []
	print "length of links", len(links)
	for i, link in enumerate(links):
		if (i + 1) % 50 == 0:
			print "article scraped", i
			time.sleep(30)
		req = requests.get(link)
		if req.status_code == 200:
			soup = BeautifulSoup(req.text)
			try:
				text = ' '.join([str(re.sub('[^\w\s]+', ' ', par.text)) for par in soup.findAll('div', {'itemprop': 'articleBody'})[0].findAll('p')])
			except IndexError:
				continue
			text = text.replace('ADVERTISEMENT', ' ')
			articles.append(text)
			pub_dates.append(soup.findAll('time')[0]['datetime'])
			final_links.append(link)
		else:
			print "sleeping"
			time.sleep(5)
	return articles, pub_dates, final_links

if __name__ == '__main__':
	search_term = sys.argv[1]
	print search_term
	links = get_links(search_term)
	articles, pub_dates, links = get_articles(links)
	frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'Fox', 'publish_date' : pub_dates, 'category' : search_term}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])	
	#frame = frame[frame['text'].apply(len) > 500]
	#frame = frame[frame['text'].apply(lambda x: search_term in x)]
	frame.to_csv('data/fox_' + search_term + '_data.csv', index = False)

