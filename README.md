News-Bias
=========

###Step by step procedure for completing project

1. Choose key words to search for in news articles
2. All the following code snippets assume you are in the News-Bias directory

Scrape data with the following lines 


`python scrapers/npr_scrape.py <search_term>`
`python scrapers/nyt_scrape.py <search_term>`
`python scrapers/fox_scrape.py <search_term>`

You can edit the code to change the dates and the number of articles returned. This also accepts multiple word searches but must have spaces escaped with a blackslash

3. The three scripts above will each ouput a csv in the data folder. The files will be named data/npr_search_term_data.csv. 

4. This data will need to be cleaned up a bit 

`python cleaned_scraped_data.py`

This script also adds sentiment scores based on a popular sentiment dictionary
This will output a file named combined_<major_category>.csv

5. At this point a manual inspection of the data must be done using NMF to determine how many sub-topics there are and what the name of these subtopics are going to be. I used a random state of 1 to generate the same subtopics each time NMF was ran. 


6. Run file explore_nmf_topics.py arg1 arg2

where arg1 is the topic you want to explore and arg2 is the number of topics you want to parse out. This is an iterative process and will take many iterations to get a number of distinct topics that you feel comofortable with. This file will output a bar graph with nmf scores next to the top 15 words for each topic. It should be relatively easy to see what the probable topics are. The graphs are stored in data/explore_nmf_topics/explore_<major category>.png

This script also stores the nmf, the nmf matrix and the tf-idf vectorizer objects as pickles to access them later

7. Once the number of topics is chosen, go into data/subtopics/<major category>_subtopics.txt and put in order the topics that match up to the bar graph


8. Next run  attach_subtopics.py <major category> to append the hand created topics. This script will output a file data/combined_<major category>_subtopics.csv

This will also output the same graph as above but with the newly labeled topic in graphs/final_<major category>.png

9. We have topics which is nice but we need a way to label the articles within these topics as positive or negative. There is already a sentiment score attached for each article but this is not domain specific. For instance - captured for the 'drug cartel' category would be a very positive event and possibly a negative event elsewhere. 

So, to deal with this domain specificity, a list of words is ouputted into a csv from a stemmed list of words of a new tf-idf vectorizer for the specific topic at hand. The top 200 words must be evaluated by hand. For each subtopic there will be a list that needs to be hand graded on some scale. I am choosing -5 to 5. These files are stored in data/keywords/key_words_<major category>_<subtopic>.csv

10. Once you think you have correctly categorized the list of key words for each subtopic (this will take a long time) you will run attach_event_score.py <major category>

This will grade each article based on its top 20 tf-idf stemmed words according to the grade you gave it.

