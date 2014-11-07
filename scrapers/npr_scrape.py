import requests
import re
import pandas as pd
from dateutil import parser
import time
import sys


def get_articles(base, key, search_word):
    full_article = []
    links = []
    pub_dates = []
    endDate = '20141105'
    startDate = '20141001'
    while endDate > startDate:
        params = {'apiKey' : key, 'output': 'JSON', 'endDate' : endDate, 'searchTerm' : search_word}
        req = requests.get(base, params=params)
        if req.status_code == 200:
            j = req.json()
            if not j.has_key('list'):
                continue
            if not j['list'].has_key('story'):
                continue
            for story in j['list']['story']: #i think there is only 1 story so might not need loop
                try:
                    text = ' '.join([par['$text'] for par in story['text']['paragraph']])
                    pub_date = endDate =  parser.parse(story['pubDate']['$text']).strftime("%Y%m%d")
                except KeyError:
                    text = ''
                    for par in story['text']['paragraph']:
                        text += par.get('$text', '')
                if len(text) < 500:
                    continue
                full_article.append(str(re.sub('[^\w\s]+', '', text)))
                links.append(story['link'][0]['$text'])
                pub_dates.append(pub_date)
        else:
            print "Sleepy..."
            # account for rate limiting
            time.sleep(2)

    return full_article, links, pub_dates

if __name__ == '__main__':
    search_word = sys.argv[1]
    key = 'MDE3MzEyOTEwMDE0MTUxMjU4MjczNTcwMw001'
    base = 'http://api.npr.org/query'
    articles, links, pub_dates = get_articles(base, key, search_word)
    frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'NPR', 'publish_date': pub_dates, 'category' : search_word}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])
    #frame = frame[frame['text'].apply(len) > 500]
    #frame = frame[frame['text'].apply(lambda x: search_word in x)]
    #frame = frame.drop_duplicates()
    frame.to_csv('data/npr_' + search_word + '_data.csv', index=False)

