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

You can edit the code to change the dates and the number of articles returned

3. The three scripts above will each ouput a csv in the data folder. The files will be named data/npr_search_term_data.csv. 

4. This data will need to be cleaned up a bit 

`python cleaned_scraped_data.py`

This script also adds sentiment scores based on a popular sentiment dictionary

5. Combine all data with sentiment scores with the following script

`python get_sub_categories.py`

This creates a csv called data/combined_data_subcategory.csv
