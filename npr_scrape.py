import requests
import re
import pandas as pd


def get_articles(base, key):
    full_article = []
    links = []
    for i in range(1000):
        params = {'apiKey' : key, 'output': 'JSON', 'startDate' : '2014-01-01', \
            'endDate' : '2014-08-01', 'startNum' : i * 10 + 1}
        req = requests.get(base, params=params)
        j = req.json()
        if not j.has_key('list'):
            continue
        if not j['list'].has_key('story'):
            continue
        for story in j['list']['story']: #i think there is only 1 story so might not need loop
            try:
                text = ' '.join([par['$text'] for par in story['text']['paragraph']])
            except KeyError:
                text = ''
                for par in story['text']['paragraph']:
                    text += par.get('$text', '')
            if len(text) < 200:
                continue
            full_article.append(str(re.sub('[^\w\s]+', '', text)))
            links.append(story['link'][0]['$text'])
    return full_article, links

if __name__ == '__main__':
    key = 'MDE3MzEyOTEwMDE0MTUxMjU4MjczNTcwMw001'
    base = 'http://api.npr.org/query'
    articles, links = get_articles(base, key)
    frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'NPR', 'rating' : .2}, \
             columns = ['source', 'url', 'text', 'rating'])
    frame.to_csv('npr_data.csv', index=False)

