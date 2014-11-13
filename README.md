News-Bias
=========

Go to the live version of the [bias detector] (http://greeksquared.pythonanywhere.com)


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

5. At this point a manual inspection of the data must be done using NMF to determine how many sub-topics there are and what the name of these subtopics are going to be. I used a random state of 1 to generate the same subtopics each time NMF was ran. Once the subtopics were chosen, they were saved in a text file.

Need to pickle the nmf object to more quickly label the subtopics

5. NMF is used to get subcategories from the major topic

`python get_sub_categories.py`

This script attaches the subtopics found above will furnish a file named <major_category>_subtopics.csv and will print out a bar graph of all the subtopics with their associated key words

