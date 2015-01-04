'''
Attempt at getting meta data from html but found other methods. This file not used.
'''


import os
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
 
path = 'data/event_scores'
listing = os.listdir(path)

for i, infile in enumerate(listing):
    print "file num", i
    print infile[:-16]
    image_urls = []
    titles = []
    descriptions = []
    df = pd.read_csv(path + '/' + infile)
    urls = df['url'].values
    for j, url in enumerate(urls):
        if j % 10 == 0:
            print "url num", j
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            u = soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content']
            image_urls.append(u)
        except IndexError:
            image_urls.append('#')
        try:
            tit = soup.findAll(attrs =  {'property' : 'og:title'})[0].attrs['content']
            titles.append(str(re.sub('[^\w\s]+', ' ', tit)))
        except IndexError:
            titles.append('None')
        try:
            desc = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
            descriptions.append(str(re.sub('[^\w\s]+', ' ', desc)))
        except IndexError:
            descriptions.append('None')
        
    df['formal_title'] = titles
    df['image_urls'] = image_urls
    df['descriptions'] = descriptions
    df.to_csv('data/completed/' + infile[:-16] + '_completed.csv', index=False)