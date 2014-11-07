import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from itertools import izip
import time
import sys


def get_links(search_word):
    api_key = "06085d751562b32ec4929cc0537bf9cc:8:69947278"
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?sort=newest&api-key=' + api_key + '&q=' + search_word
    api = requests.get(url)
    total_articles = articles_left = api.json()['response']['meta']['hits']


    max_pages = 10000
    page = 0
    final_page = 0
    page_count = 0
    cursor_count = 0
    articles_left = total_articles
    last_date = "20141105"
    latest_article = last_date
    earliest_date = "20090101"

    links = []
    pub_dates = []
    # let us loop (and hopefully not hit our rate limit)
    while articles_left > 0 and page_count < max_pages and latest_article >= earliest_date:
        more_articles = requests.get(url + "&page=" + str(page) + "&end_date=" + str(last_date))
        if page_count % 10 == 0:
            print "Inserting page " + str(page_count)
        # make sure it was successful
        if more_articles.status_code == 200:
            for content in more_articles.json()['response']['docs']:
                latest_article = parser.parse(content['pub_date']).strftime("%Y%m%d")
                pub_dates.append(latest_article)
                links.append(content.get('web_url', ''))
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
    return links, pub_dates

def get_articles(links, pub_dates):
    articles = []
    new_links = []
    new_dates = []
    for i, link in enumerate(links):
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
            text = str(re.sub('[^\w\s]+', '', text))
            text = str(re.sub('[\n]+', '', text))
            if len(text) < 500:
                continue
            articles.append(text)
            new_links.append(link)
            new_dates.append(pub_dates[i])
        else:
            print "Sleepy..."
            # account for rate limiting
            time.sleep(2)
    return new_links, articles, new_dates

if __name__ == '__main__':
    search_word = sys.argv[1]
    links, pub_dates = get_links(search_word)
    links, articles, pub_dates = get_articles(links, pub_dates)
    frame = pd.DataFrame({'text' : articles, 'url' : links, 'source' : 'NYT', 'publish_date' : pub_dates, 'category' : search_word}, \
             columns = ['source', 'url', 'text', 'publish_date', 'category'])
    #frame = frame[frame['text'].apply(lambda x: search_word in x)]
    #frame = frame.drop_duplicates()
    frame.to_csv('data/nyt_' + search_word + '_data.csv', index=False)


