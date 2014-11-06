import pandas as pd


def create_user_df():
	cnn = pd.read_csv('data/cnn_data.csv')
	cnn['user_rating'] = 0
	cnn['num_users'] = 0
	cnn.to_csv('data/cnn_user.csv', index=False)

	npr = pd.read_csv('data/npr_data.csv')
	npr['user_rating'] = 0
	npr['num_users'] = 0
	npr.to_csv('data/npr_user.csv', index=False)

	fox = pd.read_csv('data/fox_data.csv')
	fox['user_rating'] = 0
	fox['num_users'] = 0
	fox.to_csv('data/fox_user.csv', index=False)

if __name__ == '__main__':
	create_user_df()