import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

def get_soup():
	req = requests.get('http://www.foxnews.com/about/rss/')
	soup = BeautifulSoup(req.text)
	return soup

def get_topic_links(soup):
	article_div = soup.findAll('div', {'class': 'section-mod'})[0]
	all_links = article_div.findAll('a')
	topic_links = [url.attrs['data-url'] for url in all_links]
	return topic_links

def get_article_text(topic_links):
	all_articles = []
	topics = []
	urls = []
	for link in topic_links:
	    req = requests.get(link)
	    soup = BeautifulSoup(req.text, 'html.parser')
	    sublinks =  [link.text for link in soup.findAll('link') if link.text.count('/') > 3]
	    for sublink in sublinks:
	        req = requests.get(sublink)
	        soup = BeautifulSoup(req.text, 'html.parser')
	        text_soup = soup.findAll('div', {'itemprop': 'articleBody'})
	        if not text_soup:
	            print 'nothing here'
	            continue
	        
	        text = ' '.join([par.text for par in soup.findAll('div', {'itemprop': 'articleBody'})[0].findAll('p')])
	        text = str(re.sub('[^\w\s+]', '', text))
	        urls.append(req.url)
	        topics.append(urls[-1].split('/')[3])
	        all_articles.append(text)
	return urls, topics, all_articles

if __name__ == '__main__':
	soup = get_soup()
	topic_links = get_topic_links(soup)
	urls, topics, all_articles = get_article_text(topic_links)
	frame = pd.DataFrame({'text' : all_articles, 'url' : urls, 'source' : 'Fox', 'topic':topics, 'rating' : .7}, \
             columns = ['source', 'url', 'topic', 'text', 'rating'])
	frame.to_csv('fox_data.csv', index = False)

