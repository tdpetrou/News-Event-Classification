import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

def get_articles():
	urls = []
	articles = []
	for i in range(1000):
	    req = requests.get('https://en.wikipedia.org/wiki/Special:Random')
	    soup = BeautifulSoup(req.text)
	    paragraphs =  soup.findAll("div", {"id" : "mw-content-text"})[0].findAll('p')
	    text = ' '.join([par.text for par in paragraphs] )
	    text = str(re.sub('[^\w\s\[\]+]', '', text))
	    text = str(re.sub("\[.*\]", '', text))
	    if len(text) < 1000:
	    	continue
	    articles.append(text)
	    urls.append(req.url)
	return urls, articles

if __name__ == '__main__':
	urls, articles = get_articles()
	frame = pd.DataFrame({'text' : articles, 'url' : urls, 'source' : 'Wikipedia', 'rating' : 0}, columns = ['source', 'url', 'text', 'rating'])
	frame.to_csv('wikipedia_data.csv', index=False)