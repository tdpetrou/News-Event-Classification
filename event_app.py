'''
This is the major front end publishing code that uses flask to neatly return the top scored 
articles from each category to the index page. A sql query is run on page load that returns the top 
scored article from each subcategory. There are around 22 event types that are used. Many of the less
interesting event types are disregarded. It randomly displays 6 of 
these articles to be in the carousel and 4 to be in the side panel at the top. It then displays at
most 8 articles for each event type and allows the user to scroll to view all of them.
'''
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
from sqlalchemy import create_engine
import sys
import traceback
import MySQLdb

# path = '/home4/gamethe2/public_html/newventify'
# if path not in sys.path:
#     sys.path.append(path)
good_subtopics = {'Coverage and Benefits':[0, 1], 'Drug Cartels': [0, 1], 'Medical Legalization':[0, 1], 
            'Legislation' :[0, 1], 'Social Interests' : [1], 'Immigration': [0,1], 'Armed Forces': [1], 
            'Second Amendment':[1], 'Domestic Violence':[1], 'Israel vs Palestine': [0, 1], 'Rights' :[0, 1],
            'Abortion Clinics and Health': [0,1], 'Religious View on Abortion':[1], 'Middle East': [0,1]}

subtopic_map = {'Coverage and Benefits' : 'Obamacare', 'Drug Cartels': 'Marijuana', 'Medical Legalization':'Marijuana', 
            'Legislation' :'Gay Rights', 'Rights' : "Gay Rights", 'Social Interests' : 'Gay Rights', 
            'Immigration': 'Immigration', 'Armed Forces': 'Terrorism', 'Second Amendment': 'Guns', 
            'Domestic Violence': 'Guns', 'Israel vs Palestine': 'Palestine',
            'Abortion Clinics and Health': 'Abortion', 'Religious View on Abortion': 'Abortion', 
            'Middle East': 'Terrorism'}

topic_map = { 'Obamacare':['Coverage and Benefits'], 'Marijuana': ['Drug Cartels','Medical Legalization'], 
            'Gay Rights' :['Legislation','Rights','Social Interests'], 
            'Immigration': ['Immigration'], 'Terrorism': ['Armed Forces', 'Middle East'], 'Guns' :['Second Amendment','Domestic Violence'],
            'Palestine': ['Israel vs Palestine'], 'Abortion': ['Abortion Clinics and Health', 'Religious View on Abortion']}

#get sides
categories = ['abortion', 'aca', 'gay', 'gun', 'immigration', 'marijuana', 'palestine', 'terrorism']
sides = ''
for cat in categories:
    with open('data/subtopics/' + cat.replace(' ', '_') + '_sides.txt') as sides_json:
        for side in sides_json:
            sides += side[:-2]
            sides += ','
sides = sides.replace('{', '')
sides = sides.replace('}', '')
sides = '{' + sides[:-1] + '}'
sides_dict = json.loads(sides)

app = Flask(__name__)



# our home page
@app.route('/')
def index():
    with open('data/ted.txt') as f:
        password =  [line for line in f][0]

    engine = create_engine('mysql://gamethe2:' + password + '@box969.bluehost.com/gamethe2_EventClassify', pool_recycle=True)
    connection = engine.connect()
    statement = "select * " + \
        "from ( " + \
        "SELECT    u.*, " + \
        "( " + \
                    "CASE u.subcategory " + \
                    "WHEN @curType " + \
                    "THEN @curRow := @curRow + 1 " + \
                    "ELSE @curRow := 1 AND @curType := u.subcategory END " + \
                  ") + 1 AS rank, 1 as 'event_type' " + \
        "FROM      unique_url u, " + \
                  "(SELECT @curRow := 0, @curType := '') r " + \
        "where num_words > 300 and publish_date > DATE_ADD(curdate(), interval -7 day) and length(image_url) > 10 " + \
        "ORDER BY  u.subcategory, u.`event score scaled` desc ) as u2 " + \
        "where rank = 1 " + \
        "union " + \
        "( " + \
        "select * " + \
        "from ( " + \
        "SELECT    u.*, " + \
        "( " + \
                    "CASE u.subcategory " + \
                    "WHEN @curType " + \
                    "THEN @curRow := @curRow + 1 " + \
                    "ELSE @curRow := 1 AND @curType := u.subcategory END " + \
                  ") + 1 AS rank, 0 as 'event_type' " + \
        "FROM      unique_url u, " + \
                  "(SELECT @curRow := 0, @curType := '') r " + \
        "where num_words > 300 and publish_date > DATE_ADD(curdate(), interval -7 day) and length(image_url) > 10 " + \
        "ORDER BY  u.subcategory, u.`event score scaled`) as u2 " + \
        "where rank = 1 " + \
        ") " + \
        "order by subcategory "
    result = connection.execute(statement)

    return_df = pd.DataFrame(result.fetchall())
    return_df.columns = result.keys()

    return_df = return_df[return_df.apply(lambda x: good_event(x, good_subtopics), axis = 1)]



    #attach the type of event (side)
    return_df['event_descr'] = return_df.apply(lambda x: sides_dict[x['subcategory']][x['event_type']], axis = 1)
    return_df['description'] = return_df['description'].apply(lambda x: x.replace('\r', '')[:250] + '...')
    return_df = return_df.ix[np.random.permutation(return_df.index)]

    return render_template('home_page_headline.html', image_url = return_df['image_url'].values, 
        title = return_df['title'].values, description = return_df['description'].values, 
        url = return_df['url'].values, date = return_df['publish_date'].values, sides = return_df['event_descr'].values, 
        category = return_df['category'].values, source= return_df['source'].values, 
        subcategory = return_df['subcategory'].values)

def good_event(row, good_subtopics):
    subcategory = row['subcategory']
    event_type = row['event_type']
    if (subcategory in good_subtopics) and (event_type in good_subtopics[subcategory]):
        return True
    return False

@app.route('/_get_next_topic')
def _get_next_topic():
    # with open('/home4/gamethe2/public_html/newventify/data/subtopics/' + category + '_subtopics.txt', 'r') as f:
    with open('data/ted.txt') as f:
        password =  [line for line in f][0]

    engine = create_engine('mysql://gamethe2:' + password + '@box969.bluehost.com/gamethe2_EventClassify', pool_recycle=True)
    connection = engine.connect()

    test_cat = good_subtopics.items()[0]
    subcategory = test_cat[0]
    event_types = test_cat[1]
    statement = "select * from (SELECT    u.*, ( CASE u.subcategory WHEN @curType THEN @curRow := @curRow + 1 " + \
                    "ELSE @curRow := 1 AND @curType := u.subcategory END ) + 1 AS rank, 1 as 'event_type' " + \
                    "FROM unique_url u, (SELECT @curRow := 0, @curType := '') r where num_words > 300 and " + \
                    "publish_date > DATE_ADD(curdate(), interval -7 day) and length(image_url) > 10 " + \
                    "and `event score scaled` > .5 ORDER BY " + \
                    "u.subcategory, u.`event score scaled` desc ) as u2 where rank <= 8 " + \
                    "union select * from (SELECT    u.*, ( CASE u.subcategory WHEN @curType THEN @curRow := @curRow + 1 " + \
                    "ELSE @curRow := 1 AND @curType := u.subcategory END ) + 1 AS rank, 0 as 'event_type' FROM " + \
                    "unique_url u, (SELECT @curRow := 0, @curType := '') r where num_words > 300 and " + \
                    "publish_date > DATE_ADD(curdate(), interval -7 day) and length(image_url) > 10  " + \
                    "and `event score scaled` < .5 " + \
                    "ORDER BY  u.subcategory, u.`event score scaled` ) as u2 where rank <= 8"

    result = connection.execute(statement)

    return_df = pd.DataFrame(result.fetchall())
    return_df.columns = result.keys()
    topics = ['Marijuana', 'Abortion', 'Terrorism', 'Obamacare', 'Gay Rights', 'Guns', 'Palestine', 'Immigration']
    return_html = '<div class = "outer-topic-div">'
    for topic in topics:
        subcats = topic_map[topic]
        print topic, subcats
        return_html += '<div class = "big-topic-div" id = "' + topic.split()[0].lower() + '"><h2 class = "topic-header-below">' + topic + '</h2>'

        for subcat in subcats:
            vals = good_subtopics[subcat]
            for val in vals:
                current_df = return_df[return_df.apply(lambda x: subcat == x['subcategory'] and x['event_type'] == val, axis = 1)]
                return_html += '<h3 class = "bottom-title">' + sides_dict[subcat][val] +'</h3><div class ="row-other-articles-below">'
                
                for index, row in current_df.iterrows():
                    return_html += '<div class= "individualArticleBelow">' + \
                        '<a href = "' + row['url'] + '" target = "_blank">' + \
                        '<img class="img-medium-below" src= "' + row['image_url'] + '"' + \
                        'alt="Generic placeholder image"></a>' + \
                        '<div class = "article_date"><p>' + row['source'] + ' - ' + row['publish_date'] +  '</p></div>' + \
                        '<a href = "' + row['url'] + '" target = "_blank"><h5 class = "article_title">' + row['title'] + '</h5></a></div>'
                
                return_html += "</div>"
        return_html += '</div>'
    return_html += '</div>' + '<script>     $(document).ready(function(){ ' + \
                '$(".row-other-articles-below").slick({ infinite: true, slidesToShow: 4,' + \
                      'slidesToScroll: 1, }); });</script>'
    return return_html


@app.route('/_get_subtopics')
def get_subtopics():
    category = request.args.get('category', '', type=str)
    category = category.lower().replace(' ', '_')
    # with open('/home4/gamethe2/public_html/newventify/data/subtopics/' + category + '_subtopics.txt', 'r') as f:


    with open('data/subtopics/' + category + '_subtopics.txt', 'r') as f:
        all_sub_cats = [line[:-1] for line in f]
    return jsonify(result=all_sub_cats)

@app.route('/_show_time')
def show_time():
    return render_template('drop_down_time.html')


@app.route('/_get_subtopic_data')
def get_subtopic_data():
    subtopic = request.args.get('subtopic', '', type=str)
    category = request.args.get('category', '', type=str)
    subtopic_text = request.args.get('subtopic_text', '', type=str)
    days = request.args.get('days', '', type=str)
    subtopic_cat = subtopic.lower().replace(' ', '_')
    category = category.lower().replace(' ', '_')
    
    # with open('/home4/gamethe2/public_html/newventify/data/subtopics/' + category + '_sides.txt') as json_data:
    with open('data/subtopics/' + category + '_sides.txt') as json_data:
        sides = json.load(json_data)
    both_sides = sides[subtopic]

    # with open('/home4/gamethe2/public_html/newventify/data/ted.txt') as f:
    with open('data/ted.txt') as f:
        password =  [line for line in f][0]
    # engine = create_engine('mysql://EventClassify:' + password + '@EventClassify.db.5920383.hostedresource.com/EventClassify', pool_recycle=True)
    engine = create_engine('mysql://gamethe2:' + password + '@box969.bluehost.com/gamethe2_EventClassify', pool_recycle=True)
    # engine = create_engine('mysql://gamethe2:' + password + '@localhost/gamethe2_EventClassify', pool_recycle=True)
    connection = engine.connect()

    statement = "(SELECT max(source) as source, max(url) as url, max(image_url) as image_url, " + \
                "title, max(left(description, 250)) as description, max(publish_date) as publish_date," + \
                " max(`event score scaled`) as `event score scaled` FROM `unique_url` " +  \
                "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
                "' and publish_date > DATE_ADD(curdate(), interval -" + days + " day) " + \
                " and num_words > 300 " + \
                " group by title order by `event score scaled` limit 14)" + \
            " union " + \
            "(SELECT  max(source) as source, max(url) as url, max(image_url) as image_url, " + \
            " title, max(left(description, 250)) as description, max(publish_date) as publish_date," + \
            " max(`event score scaled`) as `event score scaled` FROM `unique_url` " +  \
            "WHERE category = '" + category +  "' and subcategory = '" + subtopic + \
            "' and publish_date > DATE_ADD(curdate(), interval -" + days + " day) " + \
             " and num_words > 300 " + \
            " group by title order by `event score scaled` desc limit 14) " + \
            "ORDER BY `event score scaled` "
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
    
    app.run(host='0.0.0.0', port=4444, debug=True)