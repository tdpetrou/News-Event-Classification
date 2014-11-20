#write to mysql db
import MySQLdb
import pandas as pd
import os

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
with open('data/ted.txt') as f:
	password =  [line for line in f][0]

import MySQLdb
from sqlalchemy import create_engine
'dialect+driver://username:password@host:port/database'
engine = create_engine('mysql://EventClassify:' + password + '@EventClassify.db.5920383.hostedresource.com/EventClassify', pool_recycle=True)
connection = engine.connect()
# connection.execute('drop table if exists test_event')
connection.execute('delete from test_event3')

start = 0
rows_at_a_time = 50
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

