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

app = Flask(__name__)



# our home page
@app.route('/')
def index():
    return render_template('home_page_headline.html')

@app.route('/_get_subtopics')
def get_subtopics():
    category = request.args.get('category', '', type=str)
    category = category.lower().replace(' ', '_')
    with open('data/subtopics/' + category + '_subtopics.txt', 'r') as f:
        all_sub_cats = [line[:-1] for line in f]
    # print all_sub_cats
    return jsonify(result=all_sub_cats)


@app.route('/_get_subtopic_data')
def get_subtopic_data():
    subtopic = request.args.get('subtopic', '', type=str)
    category = request.args.get('category', '', type=str)
    subtopic_text = request.args.get('subtopic_text', '', type=str)
    subtopic_cat = subtopic.lower().replace(' ', '_')
    category = category.lower().replace(' ', '_')
    
    with open('data/subtopics/' + category + '_sides.txt') as json_data:
        sides = json.load(json_data)
    both_sides = sides[subtopic]

    with open('data/ted.txt') as f:
        password =  [line for line in f][0]
    # engine = create_engine('mysql://EventClassify:' + password + '@EventClassify.db.5920383.hostedresource.com/EventClassify', pool_recycle=True)
    engine = create_engine('mysql://gamethe2:' + password + '@box969.bluehost.com/gamethe2_EventClassify', pool_recycle=True)
    connection = engine.connect()
    statement = "(SELECT  max(source) as source, max(url) as url, max(image_url) as image_url, " + \
                "title, max(left(description, 250)) as description, max(publish_date) as publish_date," + \
                " max(`event score scaled`) as `event score scaled` FROM `unique_url` " +  \
                "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
                    "' group by title order by `event score scaled` limit 14)" + \
            " union " + \
            "(SELECT * FROM" + \
            "(SELECT  max(source) as source, max(url) as url, max(image_url) as image_url, " + \
            " title, max(left(description, 250)) as description, max(publish_date) as publish_date," + \
            " max(`event score scaled`) as `event score scaled` FROM `unique_url` " +  \
            "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
            "' group by title order by `event score scaled` desc limit 14) as temp " + \
            "ORDER BY `event score scaled`)"
    result = connection.execute(statement)
    print statement
    return_df = pd.DataFrame(result.fetchall())
    return_df.columns = result.keys()
    print return_df['event score scaled'].values
    return render_template('subtopic_headlines.html', image_url = return_df['image_url'].values, 
        title = return_df['title'].values, description = return_df['description'].values, 
        url = return_df['url'].values, date = return_df['publish_date'].values, sides = both_sides, 
        category = category, subtopic = subtopic_text, source= return_df['source'].values,
        link_count = len(return_df['url'].values), link_count_half = len(return_df['url'].values) / 2)

@app.route('/_display_tables')
def display_tables():
    subtopic = request.args.get('subtopic', '', type=str)
    category = request.args.get('category', '', type=str)
    subtopic_text = request.args.get('subtopic_text', '', type=str)
    subtopic_cat = subtopic.lower().replace(' ', '_')
    category = category.lower().replace(' ', '_')
    return render_template('top_article_tables.html')


if __name__ == '__main__':
    #comments below are for pythonanywhere
    ######## WSGI Web file #############
    # import sys
    # path = '/home/greeksquared/News-Event-Classification'
    # if path not in sys.path:
    #     sys.path.append(path)
    # from event_app import app as application
    
    app.run(host='0.0.0.0', port=7070, debug=True)