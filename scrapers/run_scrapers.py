#run all the srapers
from fox_scrape import fox_scrape
from msnbc_scrape import msnbc_scrape
from npr_scrape import npr_scrape
from nyt_scrape import nyt_scrape


if __name__ == '__main__':
	# fox = fox_scrape('gay')
	# fox.run()
	# msnbc = msnbc_scrape('gay', 5)
	# msnbc.run()
	# npr = npr_scrape('gay', 7)
	# npr.run()
	nyt = nyt_scrape('gay', 1)
	nyt.run()
