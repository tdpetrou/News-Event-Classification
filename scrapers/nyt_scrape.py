import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from itertools import izip
import time
import sys


class nyt_scrape():

    def __init__(self, search_word):
        '''
        initializes api key, base url and search term
        '''
        self.api_key = "06085d751562b32ec4929cc0537bf9cc:8:69947278"
        self.search_word = search_word
        self.base_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?sort=newest&api-key=' + self.api_key + \
                '&fq=source:("The New York Times") AND (body:"' + self.search_word + '")  AND (word_count:>200)'
        self.links = []
        self.pub_dates = []
        self.word_counts = []
        self.titles = []

    def get_links(self):
        '''
        saves a list of links and publish dates to lists from object instance
        returns nothing
        '''
        api = requests.get(self.base_url)
        total_articles = articles_left = api.json()['response']['meta']['hits']

        max_pages = 300
        page = 0
        final_page = 0
        page_count = 0
        cursor_count = 0
        articles_left = total_articles
        last_date = "20141105"
        latest_article = last_date
        earliest_date = "20070101"

        # let us loop (and hopefully not hit our rate limit)
        while articles_left > 0 and page_count < max_pages and latest_article >= earliest_date:
            more_articles = requests.get(self.base_url + "&page=" + str(page) + "&end_date=" + str(last_date))
            if page_count % 10 == 0:
                print "Inserting page " + str(page_count)
            # make sure it was successful
            if more_articles.status_code == 200:
                for content in more_articles.json()['response']['docs']:
                    latest_article = parser.parse(content['pub_date']).strftime("%Y%m%d")
                    self.pub_dates.append(latest_article)
                    self.links.append(content.get('web_url', ''))
                    print "word count", content['word_count']
                    self.word_counts.append(content['word_count'])
                    self.titles.append(content['headline']['main'])
                articles_left -= 10
                page += 1
                page_count += 1
                cursor_count += 1
                final_page = max(final_page, page)
            else:
                if more_articles.status_code == 403:
                    print "Sleepy..."
                    # account for rate limiting
                    time.sleep(2)
                elif cursor_count > 100:
                    print "Adjusting date"
                    cursor_count = 0
                    page = 0
                    last_date = latest_article
                else:
                    print "ERRORS: " + str(more_articles.status_code)
                    cursor_count = 0
                    page = 0
                    last_date = latest_article

    def get_articles(self):
        articles = []
        new_links = []
        new_dates = []
        new_word_counts = []
        new_titles = []
        articles_scraped = 0
        print "number of links", len(self.links)
        for i, link in enumerate(self.links):
            try:
                req = requests.get(link)
            except:
                continue
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, "html.parser")
                body = soup.find_all('p', class_='story-body-text story-content')
                if len(body) == 0:
                    body = soup.findAll('p', {'class' : 'story-body-text'})
                text = ''
                for p in body:
                    text += p.text.encode('ascii','ignore')
                text = str(re.sub('[^\w\s]+', ' ', text))
                text = str(re.sub('[\n]+', ' ', text))
                if len(text) < 500:
                    print "article too short", link
                    continue
                if i % 100 == 0:
                    print "article number", i
                    time.sleep(30)
                articles.append(text)
                new_links.append(link)
                new_dates.append(self.pub_dates[i])
                new_word_counts.append(self.word_counts[i])
                new_titles.append(str(re.sub('[^\w\s]+', ' ', self.titles[i])))
                articles_scraped += 1
                print "actual articles scraped", articles_scraped
            else:
                print "Sleepy...", i, link
                # account for rate limiting
                time.sleep(3)
        self.links = new_links
        self.pub_dates = new_dates
        self.word_counts = new_word_counts
        self.titles = new_titles
        return articles

if __name__ == '__main__':
    nyt = nyt_scrape(sys.argv[1])
    print nyt.search_word
    nyt.get_links()
    # with open('data/nyt_' + nyt.search_word + '_links.txt', 'wb') as f:
    #     for link in nyt.links:
    #         f.write("%s" % link)
    #         f.write("\n")
    articles = nyt.get_articles()
    frame = pd.DataFrame({'text' : articles, 'url' : nyt.links, 'source' : 'NYT', \
        'publish_date' : nyt.pub_dates, 'category' : nyt.search_word, \
        'word_counts': nyt.word_counts, 'title': nyt.titles}, \
             columns = ['source', 'url', 'title',  'text', 'publish_date', 'category', 'word_counts'])

    frame.to_csv('data/nyt_' + nyt.search_word.replace(' ', '_') + '_data.csv', index=False)


