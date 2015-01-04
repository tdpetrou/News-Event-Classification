'''
Cleans data and finds sentiment
'''
from __future__ import division
import pandas as pd
from nltk.stem import SnowballStemmer
import re, sys
from langid import classify
from bs4 import BeautifulSoup
import ipdb
import sys
sys.path.append("/home4/gamethe2/public_html/newventify")

import os
print os.path.dirname(os.path.abspath(__file__))

class clean_data():
    def __init__(self):
        pass

    def get_sent_dict(self):
        sent = {}
        sent_stemmed = {}
        with open("data/sentiment.txt","r") as text:
            for line in text:
                key, value = line.split('\t')
                sent[key] = int(value)
                try:
                    sent_stemmed[self.snowball.stem(key)] = int(value)
                except: #ascii error
                    pass
        return sent, sent_stemmed

    def score_sentiment(self, text, sent_dict, total=False):
        total_sent = 0
        words = text.split()
        for word in words:
            total_sent += sent_dict.get(word, 0)
        if total:
            return total_sent
        return total_sent / len(words)

    def stem_text(self, text):
        return ' '.join([self.snowball.stem(word) for word in re.sub(r'[^\w\s]',' ',text).lower().split()])

    def join_data(self):
        # print os.path.dirname(os.path.abspath(__file__))
        # ipdb.set_trace()
        #add functionality to automatically detect all csv files
        nyt = pd.read_csv('data/nyt_' + self.major_category + '_data.csv').drop_duplicates()
        npr = pd.read_csv('data/npr_' + self.major_category + '_data.csv').drop_duplicates()
        fox = pd.read_csv('data/fox_' + self.major_category + '_data.csv').drop_duplicates()
        msnbc = pd.read_csv('data/msnbc_' + self.major_category + '_data.csv').drop_duplicates()
        goog = pd.read_csv('data/google_' + self.major_category + '_data.csv').drop_duplicates()
        # bing = pd.read_csv('data/bing_' + self.major_category + '_data.csv').drop_duplicates()

        combined_data = pd.concat([nyt, npr, fox, msnbc, goog])#, bing])
        combined_data['text'] = combined_data['text'].astype(str)
        combined_data = combined_data[combined_data['text'].apply(len) > 700]
        search_term = self.major_category.replace('_',' ')
        combined_data = combined_data[combined_data['text'].apply(lambda x: search_term in x.lower())]
        return combined_data

    def add_columns(self, data, sent, sent_stemmed):
        data['num_words'] = data['text'].apply(lambda x: len(x.split()))
        data['sentiment'] = data['text'].apply(lambda x: self.score_sentiment(x, sent))

        data['text_stemmed'] = data['text'].apply(self.stem_text)
        data['sentiment_stemmed'] = data['text_stemmed'].apply(lambda x: self.score_sentiment(x, sent_stemmed))

        data['sentiment_total']=data['text_stemmed'].apply(lambda x: self.score_sentiment(x, sent_stemmed, True))
        return data

    def keep_english(self, data):
        langs = data['text'].apply(lambda x: classify(x[:100])[0])
        return data[langs == 'en']

    def replace_escaped(self, text):
        REPLACEMENTS = [ 
            ("&quot;", '"'), ("&apos;", "'"), ('&lsquo;', "'"), ('&rsquo;', "'"), ('&#39;', "'"), 
            ('&#8217;', "'"), ('&#8216;', "'"), ('&#9733;', ''), ('&nbsp;', ' '), ('&raquo;', "'"), 
            ('&#039;', "'"), ('&mdash;', '-'), ('&#8212;', "'"), ('&ldquo;', "'"), ('&rdquo;', "'"), 
            ('&amp;', '&'), ('&#8221;', "'"), ('&#8220;', "'"),  ('&GT;', '>'), ('&LT;', '<'), 
            ('&ndash;', '-'), ('&#0146;', "'"), ('&#8211;', ' '), ('&#34;', ''), ('&#8230;', ''), 
            ('&eacute;', 'e'), ('&iacute;', 'i'), ('&ntilde;', 'n'), ('&ccedil;', 'c'), (''2329')
            ]

        for entity, replacement in REPLACEMENTS:
            try:
                text = str(text).replace(entity, replacement)
            except AttributeError:
                print text
        return text

    def replace_all(self, data):
        data['text'] = data['text'].apply(self.replace_escaped)
        data['title'] = data['title'].apply(self.replace_escaped)
        data['description'] = data['description'].apply(self.replace_escaped)
        return data

    def remove_nonproper_html(self, data):
        data['text'] = data['text'].apply(lambda x: BeautifulSoup(x).text)
        data['title'] = data['title'].apply(lambda x: BeautifulSoup(x).text)
        data['description'] = data['description'].apply(lambda x: BeautifulSoup(x).text)
        return data

    def increase_description(self, data):
        data['description'] = data.apply(self.more_description, axis = 1)
        return data

    def more_description(self, row):
        if row['description'] is None or len(str(row['description'])) < 10:
            try:
                return str(row['text'])[:200]
            except:
                print row['text']
                return row['text']
        else:
            return row['text']

    def run(self, category):
        self.major_category = category.replace(' ', '_')
        self.snowball = SnowballStemmer('english')
        sent, sent_stemmed = self.get_sent_dict()
        data = self.join_data()
        print data.shape, sum(data['text'].isnull())
        print data['text'].values[88]
        data = self.add_columns(data, sent, sent_stemmed)
        print data.shape, sum(data['text'].isnull())
        print 'text', data['text'].values[88]
        data = self.keep_english(data)
        print data.shape, sum(data['text'].isnull())
        print 'text', data['text'].values[88]
        data = self.replace_all(data)
        print data.shape, sum(data['text'].isnull())
        print 'text', data['text'].values[88]
        data = self.remove_nonproper_html(data)
        print data.shape, sum(data['text'].isnull())
        print 'text', data['text'].values[88]
        data = self.increase_description(data)
        print data.shape, sum(data['text'].isnull())
        print 'text', data['text'].values[88]
        data.to_csv('data/combined_' + self.major_category + '.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    category = sys.argv[1]
    clean = clean_data()
    clean.run(category)


