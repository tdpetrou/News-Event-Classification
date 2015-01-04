'''
Gets the highest and lowest total raw score for each subcategory so that it can be used to scale the articles on 
an approximately 0 to 1
'''
import os
import pandas as pd
import pdb

class Event_Score_Range():
	'''
	Only need to run thus periodically if the data significantly changes or classes change
	'''
	def __init__(self):
		pass

	def store_scores(self): 
		path = 'data/event_scores'
		listing = os.listdir(path)
		scores = []
		for i, infile in enumerate(listing):
			if infile[0] == '.':
				continue
			df = pd.read_csv(path + '/' + infile)
			
			ind = infile.index('_')
			cat = infile[:ind]
			sub =  ' '.join(infile[ind+1:-16].split('_'))
			scores.append([cat, sub, df['event score'].min(), df['event score'].max()])
			

		final_scores = pd.DataFrame(scores, columns = ['topic', 'subcategory', 'min', 'max'])
		final_scores.to_csv('data/event_score_range.csv', index=False)

if __name__ == '__main__':
	event = Event_Score_Range()
	event.store_scores()