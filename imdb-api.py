import requests
from bs4 import BeautifulSoup
import re
import random

def beautiful_request(link):
	req = requests.get(link)
	content = req.content
	return BeautifulSoup(content, 'lxml')

class IMDB:

	input_keyword = None
	LIMIT = None
	SECTIONS = None
	soup_material = None
	names_sec = None
	titles_sec = None
	keywords_sec = None

	def __init__(self, entry, limit=None, sections=['names', 'titles', 'keywords']):

		self.input_keyword = entry
		self.LIMIT = limit
		self.SECTIONS = sections

	def retrieve_details(self, link):
		
		details_dict = {}		

		res = beautiful_request(link)

		# extract storyline
		try:
			story = res.find_all('div', {'class':'inline canwrap'})[0]
			story = story.find_all('span')[0]
			details_dict['story'] = str(story)
		except:
			pass

		# extract genre
		try:
			genre = res.find_all('div', {'class':'see-more inline canwrap'})[1]
			genre = re.findall(r'genres=.+</a>', str(genre))
			for idx, g in enumerate(genre):
				genre[idx] = re.findall(r'>.+<', str(g))[0][1:-1]

			details_dict['genre'] = genre
		except:
			pass

		# extract details info
		try:
			detail = res.find_all('div', {'id':'titleDetails'})[0]
			country = re.findall(r'country_of_origin=.+</a>', str(detail))[0]
			country = re.findall(r'>.+<', str(country))[0]
			details_dict['country'] = country[1:-1]
		except:
			pass

		# extract languages list
		try:
			language = re.findall(r'primary_language=.+</a>', str(detail))
			for idx, dirty_lang in enumerate(language):
				lang = re.findall(r'>.+<', str(dirty_lang))[0]
				language[idx] = lang[1:-1]
			details_dict['language'] = language
		except:
			pass

		# extract release date info
		try:
			release_date = re.findall(r'Release Date:</h4>.+\n', str(detail))[0]
			release_date = re.findall(r'>.+\n', str(release_date))[0]
			details_dict['release date'] = release_date[2:-1]
		except:
			pass

		# extract duration time
		try:
			duration = detail.find_all('time')[0]
			duration = re.findall(r'>.+<', str(duration))[0]
			details_dict['duration time'] = duration[1:-1]
		except:
			pass

		# extract user reviews
		try:
			reviews = res.find_all('div', {'id':'titleUserReviewsTeaser'})[0]
			reviews = reviews.find_all('p')[0]
			reviews = str(reviews)[3:-4].split('<br/>')
			for idx, i in enumerate(reviews):
				if i == '': del(reviews[idx])
			
			details_dict['user reviews'] = reviews
		except:
			pass

		return details_dict

	def retrieve_titles(self, res): # scrape "Titles" section

		links = re.findall(r'<a\shref="/title/\S+">[\w\s]+</a>', str(res))

		names_dict = {}
		for idx, element in enumerate(links):
			name = re.findall(r'>[\w\s]+<', element)[0][1:-1]
			link = re.findall(r'"\S+"', element)[0][1:-1]
			names_dict[idx] = {'name': name}
			names_dict[idx]['link'] = 'https://www.imdb.com'+link
			
			details = self.retrieve_details(names_dict[idx]['link'])
			
			names_dict[idx]['details'] = details

		self.names_sec = names_dict

	def retrieve_names(self, res): # scrape "Names" section
		pass

	def retrieve_keywords(self, res): # scrape "Keywords" section
		pass

	def run(self):

		self.soup_material = beautiful_request('https://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=all'.format(self.input_keyword))
		result = self.soup_material.find_all('table', {'class':'findList'})

		if 'titles' in self.SECTIONS:
			self.retrieve_titles(result[0])

		if 'names' in self.SECTIONS:
			self.retrieve_names(result[1])

		if 'keywords' in self.SECTIONS:
			self.retrieve_keywords(result[2])

		#return self.put_together()

keyword = input()

imdb = IMDB(keyword, sections=['titles'])
imdb.run()

for i, j in imdb.names_sec.items():
	print(i, j)
