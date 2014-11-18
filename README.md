News Event Classification
=========

Access the app below

[greeksquared.pythonanywhere.com](greeksquared.pythonanywhere.com)

### What this app does

Online news sites are good at producing relavent articles when given a search term. Some sites even classify articles into subtopics. What is missing is the actual degree to which an event has occurred.  My app categorizes events for a search query into two polarizing sides. 

###Specifics

My app gives the user a list of major political and social issues (Obamacare, gun control, abortion, marijuana, etc..) to choose from. From here the user is given a choice of subtopics. If the user has chosen marijuana, the suptopics 'drug cartels', 'marijuana legalization', 'drugs in sports', 'drugs and kids', etc... would be supplied as a choice for the user.

The user would pick one of these subtopics and a list of articles would be shown. The articles would be split into two categories showing with the highest ranked articles by event shown.

For instance, for the drug cartel subtopic, articles best representing seizing, capturing and general confiscation of illegal drugs would be displayed on one side of the screen. Shown on the opposite side of the screen, would be articles best representing catostrophes caused by drug cartels.

The site is interactive and able to retrieve and display these event-focused articles.


###Step by step technical walk-through


A large cohort of articles must be created first to train the model to help precisely find subtopics

1. Run `python Event_Classify` in terminal with your list of topics that you want to classify. Articles from New York Times, NPR, Fox News and MSNBC are scraped, cleaned and combined.

2. Upon completion, you will need to generate a list of subtopics. To help you do this, run 'explore_nmf_topics.py arg1 arg2'

3. where arg1 is the topic you want to explore and arg2 is the number of topics you want to parse out. This is an iterative process and will take many iterations to get a number of distinct topics that you feel comofortable with. This file will output a bar graph with nmf scores next to the top 15 words for each topic. It should be relatively easy to see what the probable topics are. The graphs are stored in data/explore_nmf_topics/explore_<major category>.png

This script also stores the nmf, the nmf matrix and the tf-idf vectorizer objects as pickles to access them later

4. Once the number of topics is chosen, go into data/subtopics/<major category>_subtopics.txt and type in order the topics that match up to the bar graph

5. Next run  attach_subtopics.py <major category> to append the hand created topics. This script will output a file data/combined_<major category>_subtopics.csv

This will also output the same graph as above but with the newly labeled topic in graphs/final_<major category>.png

6. We have topics which is nice but we need a way to label the articles within these topics as positive or negative. There is already a sentiment score attached for each article but this is not domain specific. For instance - captured for the 'drug cartel' category would be a very positive event and possibly a negative event elsewhere. 

So, to deal with this domain specificity, a list of words is ouputted into a csv from a stemmed list of words of a new tf-idf vectorizer for the specific topic at hand. The top 200 words must be evaluated by hand. For each subtopic there will be a list that needs to be hand graded on some scale. I am choosing -5 to 5. These files are stored in data/keywords/key_words_<major category>_<subtopic>.csv

7. Once you think you have correctly categorized the list of key words for each subtopic (this will take a long time) you will run attach_event_score.py <major category>

This will grade each article based on its stemmed words according to the score you gave to each word in the article.

8. Now all articles have been given a subtopic and a score. The NMF and TFIDF vectorized models are pickled and retained for predicting and scoring in the future.

9. Now that a training set of articles has been created, new articles can be scraped, given suptopics, event scores and stored online in a mysql db.

10. This mysql db is accessed through ajax requests which then display the articles by event type on the web.



