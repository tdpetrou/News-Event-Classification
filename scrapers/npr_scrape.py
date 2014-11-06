import requests
import re
import pandas as pd


def get_articles(base, key):
    full_article = []
    links = []
    pub_dates = []
    for i in range(0,200):
        params = {'apiKey' : key, 'output': 'JSON', 'startDate' : '2001-01-01', \
            'endDate' : '2014-08-01', 'startNum' : i * 10 + 1, 'searchTerm' : 'legal marijuana'}
        req = requests.get(base, params=params)
        j = req.json()
        if not j.has_key('list'):
            continue
        if not j['list'].has_key('story'):
            continue
        for story in j['list']['story']: #i think there is only 1 story so might not need loop
            try:
                text = ' '.join([par['$text'] for par in story['text']['paragraph']])
                pub_date = story['pubDate']['$text']
            except KeyError:
                text = ''
                for par in story['text']['paragraph']:
                    text += par.get('$text', '')
            if len(text) < 500:
                continue
            full_article.append(str(re.sub('[^\w\s]+', '', text)))
            links.append(story['link'][0]['$text'])
            pub_dates.append(pub_date)
    return full_article, links, pub_dates

if __name__ == '__main__':
    key = 'MDE3MzEyOTEwMDE0MTUxMjU4MjczNTcwMw001'
    base = 'http://api.npr.org/query'
    articles, links, pub_dates = get_articles(base, key)
    frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'NPR', 'publish_date': pub_dates, 'category' : 'drugs'}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])
    frame = frame[frame['text'].apply(len) > 500]
    frame = frame[frame['text'].apply(lambda x: 'legal' in x and 'marijuana' in x)]
    frame = frame.drop_duplicates()
    frame.to_csv('data/npr_drug_data.csv', index=False)

