import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


def get_articles(base, key):
	articles = []
	links = []
	pub_date = []
	for i in range(200):
		params = {'api-key' : key, 'page' : i, 'begin_date' : '20010101', 'q' : 'legalize drug' }
		req = requests.get(base, params=params)
		try:
			docs = req.json()['response']['docs']
		except KeyError:
			continue
		for doc in docs:
			try:
				url = doc['web_url']
			except KeyError:
				continue
			req = requests.get(url)
			soup = BeautifulSoup(req.text, "html.parser")
			body = soup.find_all('p', class_='story-body-text story-content')
			if len(body) == 0:
				body = soup.findAll('p', {'class' : 'story-body-text'})
			text = ''
			for p in body:
				text += p.text.encode('ascii','ignore')
			text = str(re.sub('[^\w\s]+', '', text))
			text = str(re.sub('[\n]+', '', text))
			if len(text) < 500:
				continue
			articles.append(text)
			links.append(url)
			pub_date.append(doc['pub_date'])
	return links, articles, pub_date

if __name__ == '__main__':
	base = "http://api.nytimes.com/svc/search/v2/articlesearch.json"
	key = key = "06085d751562b32ec4929cc0537bf9cc:8:69947278"
	links, articles, pub_date = get_articles(base, key)
	frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'NYT', 'publish_date' : pub_date, 'category' : 'drugs'}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])
	frame.to_csv('data/nyt_data.csv', index=False)