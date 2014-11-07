import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

def get_links(base):
	links = []
	for i in range(10):
		req = requests.get(base + str(i * 10))
		print req.url
		soup = BeautifulSoup(req.text, 'html.parser')
		#get all links that are not videos
		links.extend([a['href'] for a in soup.findAll('a', {'class' : 'ez-title'})])# if a['href'].split('//')[1][0] != 'v'])
	return list(set(links))

def get_articles(links):
	articles = []
	pub_dates = []
	final_links = []
	print "length of links", len(links)
	for link in links:
		req = requests.get(link)
		soup = BeautifulSoup(req.text)
		try:
			text = ' '.join([str(re.sub('[^\w\s]+', '', par.text)) for par in soup.findAll('div', {'itemprop': 'articleBody'})[0].findAll('p')])
		except IndexError:
			continue
		text = text.replace('ADVERTISEMENT', ' ')
		articles.append(text)
		pub_dates.append(soup.findAll('time')[0]['datetime'])
		final_links.append(link)
	return articles, pub_dates, final_links

if __name__ == '__main__':
	base = 'http://www.foxnews.com/search-results/search?&q=abortion&sort=date&ss=fn&start='
	#base = 'http://www.foxnews.com/search-results/search?&submit=Search&q=legalize+drug&ss=fn&start='
	links = get_links(base)
	articles, pub_dates, links = get_articles(links)
	frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'Fox', 'publish_date' : pub_dates, 'category' : 'abortion'}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])	
	#frame = frame[frame['text'].apply(len) > 500]
	frame = frame[frame['text'].apply(lambda x: 'abortion' in x or 'Abortion' in x)]
	frame.to_csv('data/fox_abortion_data.csv', index = False)

