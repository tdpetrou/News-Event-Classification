#write to mysql db
import pandas as pd
import os
from sqlalchemy import create_engine

class write_to_db():

	def __init__(self):
		pass

	def run(self):
		path = 'data/event_scores/new'
		listing = os.listdir(path)

		i = 0
		for infile in listing:
			print "file num", infile
			if '.csv' in infile:
				i += 1
				if i == 1:
					df = pd.read_csv(path + '/' + infile)
				else:
					df_temp = pd.read_csv(path + '/' + infile)
					df = pd.concat([df, df_temp])


		df = df.fillna('')
		df = df.drop_duplicates()
		print df.shape

		news_source_df = pd.read_csv('data/news_source_lookup.csv', header=None)
		ns_dict = dict(news_source_df.values)
		df['source'] = df['source'].apply(lambda x: ns_dict.get(x, x))


		with open('data/ted.txt') as f:
			password =  [line for line in f][0]


		'dialect+driver://username:password@host:port/database'
		# engine = create_engine('mysql://EventClassify:' + password + '@EventClassify.db.5920383.hostedresource.com/EventClassify', pool_recycle=True)
		engine = create_engine('mysql://gamethe2:' + password + '@box969.bluehost.com/gamethe2_EventClassify', pool_recycle=True)
		connection = engine.connect()
		# connection.execute('drop table if exists test_event3')
		# connection.execute('delete from test_event3')
		df = df[df.columns - ['text', 'text_stemmed']]
		start = 0
		rows_at_a_time = 300
		finish = start + rows_at_a_time
		df_sql = df[start : finish]
		num_rows = len(df_sql)

		while num_rows > 0:
			print df_sql.shape
			print df_sql['category'].unique(), df_sql['subcategory'].unique()
			df_sql.to_sql('test_event3', engine, 'mysql', if_exists ='append')
			start = finish
			finish = start + rows_at_a_time
			df_sql = df[start : finish]
			num_rows = len(df_sql)
			print num_rows

		connection.execute('drop table if exists unique_url;')
		sql = 'CREATE TABLE `unique_url` ' + \
			'SELECT `url`, ' + \
			'max(category) as category, ' + \
			'max(description) as description, ' + \
			'max(`event score`) as `event score`, ' + \
			'max(`event score scaled`) as `event score scaled`, ' + \
			'max(image_url) as image_url, ' + \
			'max(num_words) as num_words, ' + \
			'max(publish_date) as publish_date, ' + \
			'max(sentiment) as sentiment, ' + \
			'max(sentiment_total) as sentiment_total, ' + \
			'max(source) as source, ' + \
			'max(subcategory) as subcategory, ' + \
			'max(title) as title ' + \
			'from test_event3 ' + \
			'group by `url` '
		
		connection.execute(sql)
		connection.close()
if __name__ == '__main__':
	wdb = write_to_db()
	wdb.run()

