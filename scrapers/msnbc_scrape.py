import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

def get_links(base):
	links = []
	for i in range(200):
		req = requests.get(base + str(i))
		soup = BeautifulSoup(req.text)
		#msnbc does not return the base link. must add it here
		links.extend(['http://www.msnbc.com' + a['href'] for a in soup.findAll('a', {'class': 'search-result__teaser__title__link'}) if a['href'][:6] == '/msnbc'])
	return list(set(links))

def get_articles(links):
	articles = []
	pub_dates = []
	final_links = []
	for link in links:
		req = requests.get(link)
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
	return final_links, articles, pub_dates

if __name__ == '__main__':
	base = 'http://www.msnbc.com/search/legal%20marijuana?sm_field_issues=&sm_field_show=&date[min]&date[max]&date[date_selector]=&page='
	links = get_links(base)
	links, articles, pub_dates = get_articles(links)
	frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'MSNBC', 'publish_date': pub_dates, 'category' : 'drugs'}, \
		columns = ['source', 'url', 'text', 'publish_date', 'category'])
	frame = frame[frame['text'].apply(len) > 500]
	frame = frame[frame['text'].apply(lambda x: 'legal' in x and 'marijuana' in x)]
	frame = frame.drop_duplicates()
	frame.to_csv('data/msnbc_drug_data.csv', index=False)