import requests
import re
import pandas as pd
from dateutil import parser
import time
import sys

class npr_scrape():

    def __init__(self, search_word):
        '''
        Initialize api keys and base url for NPR API query
        '''
        self.api_key = 'MDE3MzEyOTEwMDE0MTUxMjU4MjczNTcwMw001'
        self.base_url = 'http://api.npr.org/query'
        self.search_word = search_word
        self.links = []
        self.pub_dates = []
        self.titles = []
    def get_articles(self):
        '''
        Get all articles with given search word taken from system argument
        returns text of articles
        '''
        full_article = []
        endDate = '20141105'
        startDate = '20090101'
        pub_date = endDate
        art_num = 1
        start_num = 1
        while pub_date > startDate:
            params = {'apiKey' : self.api_key, 'output': 'JSON', 'endDate' : endDate, \
                'searchTerm' : self.search_word, 'startNum' : start_num, 'requiredAssets' : 'text'}

            req = requests.get(self.base_url, params=params)
            if req.status_code == 200:
                j = req.json()
                if not j.has_key('list'):  #check for keys. Some articles don't have these
                    continue
                if not j['list'].has_key('story'):
                    continue
                for story in j['list']['story']: 
                    try:
                        text = ' '.join([par['$text'] for par in story['text']['paragraph']])
                        pub_date = parser.parse(story['pubDate']['$text']).strftime("%Y%m%d")
                    except KeyError:
                        text = ''
                        if not story['text'].has_key('paragraph'):
                            continue
                        for par in story['text']['paragraph']:
                            text += par.get('$text', ' ')
                        pub_date = parser.parse(story['pubDate']['$text']).strftime("%Y%m%d")
                    if len(text) < 500:
                        continue
                    art_num += 1
                    if art_num % 50 == 0:
                        print "article scraped", art_num, endDate, startDate
                    full_article.append(str(re.sub('[^\w\s]+', ' ', text)))
                    self.links.append(story['link'][0]['$text'])
                    self.pub_dates.append(pub_date)
                    self.titles.append(str(re.sub('[^\w\s]+', ' ', story['title']['$text'])))
                start_num += 10
                if start_num > 300:
                    start_num = 1
                    endDate = min(self.pub_dates)
                    
            else:
                print "Sleepy..."
                # account for rate limiting
                time.sleep(2)

        return full_article

if __name__ == '__main__':
    npr = npr_scrape(sys.argv[1])
    articles = npr.get_articles()
    print npr.titles
    print npr.links
    frame = pd.DataFrame({'text' : articles, 'url' : npr.links, 'source' : 'NPR', 'publish_date': npr.pub_dates, 'category' : npr.search_word, 'title' : npr.titles}, columns = ['source', 'url', 'title', 'text', 'publish_date', 'category'])
    print npr.search_word.replace(' ', '')
    print frame
    print 'data/npr_' + npr.search_word.replace(' ', '_') + '_data.csv'
    frame.to_csv('data/npr_' + npr.search_word.replace(' ', '_') + '_data.csv', index=False)

