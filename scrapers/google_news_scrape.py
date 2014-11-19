import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import unicodedata
import datetime

def return_df():
    descriptions = []
    titles = []
    image_urls = []
    articles = []

    current_day = datetime.datetime.now()
    DD = datetime.timedelta(1)

    start_date = current_day.strftime('%Y-%m-%d')
    search_word = 'marijuana'
    base = create_base_url(start_date, search_word)
    req = requests.get(base)
    #req = requests.get('https://www.google.com/search?hl=en&gl=us&tbm=nws&authuser=0&q=marijuana&oq=marijuana#q=marijuana&hl=en&gl=us&authuser=0&tbm=nws&start=20&tbs=cdr%3A1%2Ccd_min%3A11%2F18%2F2014%2Ccd_max%3A11%2F18%2F2014')
    soup = BeautifulSoup(req.text, 'html.parser')
    links = []
    for a in soup.findAll('a'):
        h = a['href']
        if 'q=http' in h:
            start = h.index('http')
            end = h.index('&')
            links.append(h[start:end])

    new_links = []
    for link in links:
        try:
            req = requests.get(link)
        except:
            continue
        new_links.append(link)
        soup = BeautifulSoup(req.text, 'html.parser')
        entire_article = soup.findAll('article')
        if not entire_article:
            text = ' '.join([par.text for par in soup.findAll('p')])

        else:
            for art in entire_article:
                for par in art.findAll('p'):
                    text += par.text + ' '
        text = decode_unicode(text)
        articles.append(text)
        try:
            title = soup.findAll('meta', {'name' : 'dc.title'})[0]['content']
        except:
            try:
                title = soup.findAll('title')[0].text
            except:
                title = 'None'
        title = decode_unicode(title)
        titles.append(title)
        try:
            desc = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
            desc = decode_unicode(desc)
        except:
            desc = 'None'
        descriptions.append(desc)
        try:
            image_urls.append(soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content'])
        except IndexError:
            image_urls.append('#')

        source = get_source(req.url)
        frame = pd.DataFrame({'text' : articles, 'url' : new_links, 'source' : source, \
            'publish_date' : start_date, 'category' : search_word, \
            'title': titles, 'image_url': image_urls, 'description' : descriptions}, \
            columns = ['source', 'url', 'image_url', 'title', 'description', 'text', 'publish_date', 'category'])

        frame.to_csv('data/google_' + search_word.replace(' ', '_') + '_data.csv', index=False)
    
def get_source(url):
    pieces = []
    for seg in url.split('.'):
        for piece in seg.split('/'):
            pieces.append(piece)
    if 'com' in pieces:
        ind = pieces.index('com')
    elif 'net' in pieces:
        ind = pieces.index('net')
    elif len(pieces) >=2:
        ind = 2
    else:
        return 'None'
    return pieces[ind - 1]

def decode_unicode(text):
    text = unicode(text)
    a = '/'; b = '\''
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    text = str(re.sub('[\n]+', ' ', text))
    text = str(re.sub('[\t]+', ' ', text))
    text = text.replace(a, '')
    text = text.replace(b, '')
    return text

def create_base_url(date, search_term):
    page = 0
    date = date.split('-')
    base = 'https://www.google.com/search?hl=en&gl=us&tbm=nws&authuser=0&q='
    base += search_term + '&oq=' + search_term + '#q=' + search_term
    base += '&hl=en&gl=us&authuser=0&tbm=nws&start=' + str(page) + '&tbs=cdr%3A1%2Ccd_min%3A'
    base += date[1] + '%2F' + date[2] + '%2F' + date[0] + '%2Ccd_max%3A' + date[1] + '%2F' + date[2] + '%2F' + date[0]
    return base

if __name__ == '__main__':
    return_df()
