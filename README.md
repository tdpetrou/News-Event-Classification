News Event Classification
=========

Access the app below

[www.NewVentify.com](http://www.newventify.com)

####Screenshot of app

![alt tag](https://github.com/tdpetrou/News-Event-Classification/blob/master/static/preview.png)

### App Purpose

Online news sites are good at producing relevant articles when given a search term. Some sites even classify articles into subtopics. What is missing is the actual degree to which an event has occurred.  The image below is a Fox News search query result that is typical of major news outlets. Though the articles returned to the user are relevant to the search term, there is no method to search for the degree of the event within the topic searched.

![alt tag](https://raw.githubusercontent.com/tdpetrou/News-Event-Classification/master/static/news_search.png)

Instead of showing articles by relevance, NewVentify returns articles to the user based on degree of events contained within the search.

###Specifics

NewVentify presents the user with a list of major political and social issues (Obamacare, gun control, abortion, marijuana, etc..) to choose from. Once a major topic is selected, the user is presented a choice of subtopics. If the user has chosen marijuana, the suptopics 'drug cartels', 'marijuana legalization', 'drugs in sports', 'drugs and kids', etc... would be supplied as a choice for the user. The last step requires the user to choose a date range for the articles.

Returned to the user would be articles split into two categories showing the highest ranked articles by event shown. For instance, for the drug cartel subtopic, articles best representing seizing, capturing and general confiscation of illegal drugs would be displayed on one side of the screen. Shown on the opposite side of the screen, would be articles best representing catostrophes caused by drug cartels.

###Step by step technical walk-through

A large cohort of articles must be obtained to train the model to help precisely find subtopics

* Articles from New York Times, NPR, Fox News, MSNBC and Google news are scraped, cleaned and combined into a single csv. Articles based on 8 major topics were obtained through either the new site's api or their search engine.

* For each of the major topics a list of subtopics was generated. This was an iterative process using natural language processing to create a feature matrix based on tf-idf scores and split into topics with non-negative matrix factorization.

* Bar plots showing nmf scores next to the top 15 words for each subtopic were generaged to easily put a label to the topic. A sample bar plot for words in the 4 subtopics from the gun category are shown below.

![alt tag](https://github.com/tdpetrou/News-Event-Classification/blob/master/static/nmf_words_by_topic.png)

* Once a final group of subtopics were selected, the nmf and tf-idf objects for each subtopic were saved (pickled) to use on future articles.

* Having topics is nice but there needs to be a way to detect polarizing events within these articles. Another round of nmf can work to do this but will not work as well as a customized dictionaray. Sentiment dictionaries do not work here either as each subtopic contains particular words that are domain-specific and could mean very different things. For instance - captured for the 'drug cartel' category would be a very positive event and possibly a negative event elsewhere. 

* To deal with this domain specificity, a list of words is generted for each subtopic and graded on a scale from -5 to 5. Two events per subtopic were generated

* Now that a training set of articles has been created, new articles can be scraped, given suptopics, event scores and are stored online in a mysql db.

* This mysql db is accessed through ajax requests which then display the articles by event type on the web.

* A daily cron job is run to execute scraping, cleaning, labeling and writing to database on a daily basis.



