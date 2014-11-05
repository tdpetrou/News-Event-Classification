import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_primary_links():
	req = requests.get("http://www.cnn.com/services/rss/")
	soup = BeautifulSoup(req.text)

	links = [link['href'] for link in soup.findAll("a", href=True) if link['href'][0:14] == "http://rss.cnn"]
	more_links = [link['href'] for link in soup.findAll("link", href=True) if link['href'][0:14] == "http://rss.cnn"]
	links = list(set(links).union(set(more_links)))
	return links

def get_all_links(links):
#only run once
	sublinks = []
	for link in links:
	    tech = requests.get(link)
	    soup = BeautifulSoup(tech.text, 'html.parser')
	    sublinks.extend([link.text for link in soup.findAll('link') if link.text[:10] == 'http://rss'])
	return sublinks

def get_article_text(sublinks):
	all_articles = []
	for link in sublinks:
	    print "scraping", link
	    try:
	    	req = requests.get(link)
	    except:
	    	all_articles.append('')
	    	continue
	    soup = BeautifulSoup(req.text)
	    article_text = ''
	    for par in soup.findAll('p'): # {'class' : 'cnn_storypgraphtxt'}
	        article_text += ' ' + par.text
	    all_articles.append(article_text)
	cleaned_articles = [str(re.sub('[^\w\s]+', '', art)) for art in all_articles]
	return cleaned_articles


if __name__ == '__main__':
	links = get_primary_links()
	sublinks = get_all_links(links)
	print "sublinks", sublinks
	topics = [link.split('/')[5][4:] for link in sublinks]
	articles = get_article_text(sublinks)
	frame = pd.DataFrame({'text' : articles, 'topic' : topics, 'source' : 'CNN', 'rating' : .4}, columns = ['source', 'topic', 'text', 'rating'])
	frame.to_csv('cnn_data.csv', index=False)