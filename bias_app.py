from flask import Flask
from flask import request, render_template
import build_model, pickle
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import pickle
from alchemyapi import AlchemyAPI
import re


model = pickle.load( open( "model.pkl", "rb" ) )
vec  = pickle.load( open( "vectorizer.pkl", "rb" ) )

app = Flask(__name__)



# our home page
@app.route('/')
def index():
        return '''
            <div>
                <h2>Enter in url that you want to detect bias</h2>
                <form action="/classify_document" method='POST' >
                    <input type="text" name="user_input" size = 40 />
                    <input type="submit" />
                </form>
                
            </div>
            <div>
                <h1> <a href = '/google_yahoo_news'>Get Bias scores for Google and yahoo news</a></h1>
            </div>
            <div>
                <h1> <a href = '/Rate_Articles'>Give us your rating of bias</a></h1>
            </div>
            '''



# My word counter app
#==============================================
# create the page the form goes to
@app.route('/classify_document', methods=['POST'] )
def classify_document():
    # get data from request form, the key is the name you set in your form
    url = request.form['user_input']
    #data = data.encode('ascii', 'ignore')
    # convert data from unicode to string
    alchemyapi = AlchemyAPI()
    
    # # run a simple program that counts all the words
    # model = pickle.load( open( "model.pkl", "rb" ) )
    # vec  = pickle.load( open( "vectorizer.pkl", "rb" ) )
    
    alc = alchemyapi.text('url', url)   

    text = str(re.sub('[^\w\s]+', '', alc['text']))
    text = str(re.sub('\n+', '', text)) 


    prediction = model.predict(vec.transform([text]).toarray())[0]
    # # now return your results 
    return render_template('model_results.html', prediction = prediction)



@app.route('/google_yahoo_news')
def google_yahoo_news():
    alchemyapi = AlchemyAPI()
    r = requests.get("http://news.google.com")
    soup = BeautifulSoup(r.text, "html.parser")
    divs = [div for div in soup.findAll('div', 'esc-lead-article-title-wrapper')]
    links = []
    bias_scores = []
    for div in divs:
        link = div.find_all('a', href=True)
        links.append(link[0]['href'])
    for link in links:
        response = alchemyapi.text('url', link)
        text = str(re.sub('[^\w\s]+', '', response['text']))
        text = str(re.sub('\n+', '', text)) 
        bias_scores.append(model.predict(vec.transform([text]).toarray())[0])
    return render_template('google_news_temp.html', data = zip(links, bias_scores ))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070, debug=True)