#combine multiple topics into one
#some topics must be combined into one. do those manually here.

import pandas as pd

if __name__ == '__main__':
	a = pd.read_csv('data/combined_affordable_care_act.csv')
	o = pd.read_csv('data/combined_obamacare.csv')
	aca = pd.concat([a,o])
	aca.to_csv('data/combined_aca.csv')