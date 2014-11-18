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
import MySQLdb
from sqlalchemy import create_engine
'dialect+driver://username:password@host:port/database'



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

    with open('data/ted.txt') as f:
        password =  [line for line in f][0]
    engine = create_engine('mysql://EventClassify:' + password + '@EventClassify.db.5920383.hostedresource.com/EventClassify', pool_recycle=True)
    connection = engine.connect()
    statement = "(SELECT url, image_url, title, description, `event score scaled` FROM `test_append` " +  \
                "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
                    "' order by `event score scaled` limit 4)" + \
            " union " + \
            "(SELECT url, image_url, title, description, `event score scaled` FROM `test_append` " + \
            "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
            "' order by `event score scaled` desc limit 4)"
    result = connection.execute(statement)
    print statement
    return_df = pd.DataFrame(result.fetchall())
    return_df.columns = result.keys()
    print return_df['event score scaled'].values
    #df_top = add_meta_info(df_top)
    #df_bottom = add_meta_info(df_bottom)
    #return jsonify(side1 = both_sides[0], side2 = both_sides[1], df_bottom = list(df_bottom['event score scaled'].values)) #, df_top = df_top)
    return render_template('subtopic_headlines.html', image_url = return_df['image_url'].values, 
        title = return_df['title'].values, description = return_df['description'].values, 
        url = return_df['url'].values, sides = both_sides, category = category, subtopic = subtopic)


if __name__ == '__main__':
    #comments below are for pythonanywhere
    ######## WSGI Web file #############
    # import sys
    # path = '/home/greeksquared/News-bias'
    # if path not in sys.path:
    #     sys.path.append(path)
    # from bias_app import app as application
    
    app.run(host='0.0.0.0', port=7070, debug=True)