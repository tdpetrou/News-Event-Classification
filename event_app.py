from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import pickle
import re
import datetime
import os
import pickle
import requests
import json
import pdb

app = Flask(__name__)



# our home page
@app.route('/')
def index():
    r = requests.get('http://www.foxnews.com/politics/2014/11/15/gop-mulls-options-to-stop-obama-from-acting-alone-on-immigration-with-spending/')
    soup = BeautifulSoup(r.text, 'html.parser')
    image_url = soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content']
    title =  soup.findAll(attrs =  {'property' : 'og:title'})[0].attrs['content']
    description = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
    url = soup.findAll(attrs =  {'property' : 'og:url'})[0].attrs['content']
    #pdb.set_trace()
    return render_template('home_page_headline.html')

@app.route('/_get_subtopics')
def get_subtopics():
    category = request.args.get('category', '', type=str)
    category = category.lower().replace(' ', '_')
    with open('data/subtopics/' + category + '_subtopics.txt', 'r') as f:
        all_sub_cats = [line[:-1] for line in f]
    print all_sub_cats
    return jsonify(result=all_sub_cats)


@app.route('/_get_subtopic_data')
def get_subtopic_data():
    subtopic = request.args.get('subtopic', '', type=str)
    category = request.args.get('category', '', type=str)
    subtopic_cat = subtopic.lower().replace(' ', '_')
    category = category.lower().replace(' ', '_')
    df = pd.read_csv('data/event_scores/' + category + '_' + subtopic_cat + '_event_score.csv').sort('event score scaled')
    with open('data/subtopics/' + category + '_sides.txt') as json_data:
        sides = json.load(json_data)
    both_sides = sides[subtopic]

    df_top = df.head(4).reset_index(drop=True)
    df_bottom = df.tail(4).reset_index(drop=True)[::-1]

    r = requests.get('http://www.foxnews.com/politics/2014/11/15/gop-mulls-options-to-stop-obama-from-acting-alone-on-immigration-with-spending/')
    soup = BeautifulSoup(r.text, 'html.parser')
    image_url = soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content']
    title =  soup.findAll(attrs =  {'property' : 'og:title'})[0].attrs['content']
    description = soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content']
    url = soup.findAll(attrs =  {'property' : 'og:url'})[0].attrs['content']
    #df_top = add_meta_info(df_top)
    #df_bottom = add_meta_info(df_bottom)
    image_url = 'http://media.npr.org/assets/img/2014/04/18/warondrugs-338-c851cfc2fd32c68466d1a6e6c0b445f120379505.jpg'
    #return jsonify(side1 = both_sides[0], side2 = both_sides[1], df_bottom = list(df_bottom['event score scaled'].values)) #, df_top = df_top)
    return render_template('subtopic_headlines.html', image_url = image_url, title = title, 
        description = description, url =url)


def add_meta_info(df):
    urls = df['url'].values
    image_urls = []
    titles = []
    descriptions = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        image_urls.append(soup.findAll(attrs =  {'property' : 'og:image'})[0].attrs['content'])
        titles.append(soup.findAll(attrs =  {'property' : 'og:title'})[0].attrs['content'])
        descriptions.append(soup.findAll(attrs =  {'property' : 'og:description'})[0].attrs['content'])
    df['formal_title'] = titles
    df['image_urls'] = image_urls
    df['descriptions'] = descriptions
    return df


if __name__ == '__main__':
    #comments below are for pythonanywhere
    ######## WSGI Web file #############
    # import sys
    # path = '/home/greeksquared/News-bias'
    # if path not in sys.path:
    #     sys.path.append(path)
    # from bias_app import app as application
    
    app.run(host='0.0.0.0', port=7070, debug=True)