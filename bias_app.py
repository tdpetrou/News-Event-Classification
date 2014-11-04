from flask import Flask
from flask import request, render_template
import build_model, pickle
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

# our home page
@app.route('/')
def index():
        return '''
            <h2>Enter in the text of your article to get a bias score</h2>
            <form action="/classify_document" method='POST' >
                <input type="text" name="user_input" size = 40 />
                <input type="submit" />
            </form>
            <a href = '/'>home</a>
            '''



# My word counter app
#==============================================
# create the page the form goes to
@app.route('/classify_document', methods=['POST'] )
def classify_document():
    # get data from request form, the key is the name you set in your form
    data = request.form['user_input']
    data = data.encode('ascii', 'ignore')
    # convert data from unicode to string
    data = str(data)

    data = data.encode('ascii', 'ignore')
    
    # run a simple program that counts all the words
    model = pickle.load( open( "model.pkl", "rb" ) )
    vec  = pickle.load( open( "vectorizer.pkl", "rb" ) )
    prediction = model.predict(vec.transform([data]).toarray())[0]
    

    # now return your results 
    return render_template('model_results.html', prediction = prediction)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070, debug=True)