import requests, random, sys, os
from bs4 import BeautifulSoup
from unidecode import unidecode
from pyspark.sql import SparkSession

_max_book_id = 67577

code = requests.get("https://raw.githubusercontent.com/c-w/gutenberg/master/gutenberg/_domain_model/text.py").text
exec(code)

class Text():
	def __init__(self, max_text_id, text_url, text_id = None, min_popular = 0):
		 self.__max_text_id = max_text_id
		 self.__text_url = text_url
		 self.__text_id = text_id
		 self.__min_popular = min_popular

	def _popular(self, popular_value):
		return int(popular_value) > self.__min_popular

	def _validation(self, request):
		raise NotImplementedError

	def __find_random_text(self):
		text_id = random.randint(1, self.__max_text_id)
		return text_id, requests.get( self.__text_url.format(id = text_id), allow_redirects=False )

	def __find_text(self):
		if self.__text_id is not None:
			return self.__text_id, requests.get( self.__text_url.format(id = self.__text_id) )
		text_id, request = self.__find_random_text()
		while not self._validation(request):
			text_id, request = self.__find_random_text()
			print( "Invalid text, finding another:", request.url )
		return text_id, request

	def _clean_text(self, text):
		return unidecode( text.replace( os.linesep, ' ').strip() )

	def _clean_text_list(self, text_list):
		return [self._clean_text(paragraph) for paragraph in text_list if paragraph != '']
		return SparkSession.builder.getOrCreate().parallelize( text_list ).map( lambda paragraph: self._clean_text(paragraph) if paragraph != '' else None ).collect()

	def get_id(self):
		return self.__text_id

	def get_url(self):
		return self.__text_url.format(id = self.__text_id)

	def get_request(self):
		return self.__request

	def _extract_meta(self):
		self.__text_id, self.__request = self.__find_text()



class Book(Text):
	def __init__(self, **kwargs):
		""" 

		Examples: 
			Book()
			Book( text_id = 2701 )
			Book( min_popular = 10 )
		"""
		super().__init__(_max_book_id, "https://www.gutenberg.org/ebooks/{id}", **kwargs) #https://www.gutenberg.org/files/219/219-0.txt #'https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt'
		self.title, self.author, self.text = self._extract_meta()

	def _validation(self, request):
		if request.status_code != 200:
			return False
		soup = BeautifulSoup(request.text, "html.parser")
		loc_class = ['literature' in x.text.lower() for x in soup.find_all('tr', property="dcterms:subject")]
		language = soup.find(property="dcterms:language").find('td').text
		popular = self._popular( soup.find(itemprop = "interactionCount").text.split(maxsplit = 1)[0] )
		return language == 'English' and any(loc_class) and popular

	def _extract_meta(self):
		super()._extract_meta()
		soup = BeautifulSoup(self.get_request().text, "html.parser")
		file_url = 'https://www.gutenberg.org' + soup.find("table", class_ = "files").find_all('a', string = "Plain Text UTF-8")[0].get('href')
		file = requests.get(file_url).content.decode('utf-8')

		# Isolates the book context from the header/footer information 
		idx_start = max(file.find(marker) for marker in TEXT_START_MARKERS)
		idx_end = [file.rfind(marker, idx_start) for marker in TEXT_END_MARKERS] 
		idx_end = min([x for x in idx_end if x > -1], default = len(file))

		#text = SparkSession.builder.getOrCreate().parallize( file[idx_start:idx_end] ).map( lambda x: x.split( str(os.linesep)*2 )[1:] ).map( self._clean_text ).collect()
		text = self._clean_text_list( file[idx_start:idx_end].split( str(os.linesep)*2 )[1:] )
		
		return (soup.find(itemprop="headline").text, 
				soup.find(itemprop="creator").text, 
				text)


class FanFiction(Text):
	def __init__(self, **kwargs):
		""" 

		Examples: 
			FanFiction()
			FanFiction( text_id = 2701 )
			FanFiction( min_popular = 10 )
		"""
		super().__init__(sys.maxsize, 'https://archiveofourown.org/works/{id}?view_full_work=true', **kwargs)
		self.title, self.author, self.text = self._extract_meta()

	def _validation(self, request):
		if request.status_code != 200:
			return False
		soup = BeautifulSoup(request.text, "html.parser")
		language = soup.find("dd", class_="language").text.rstrip().lstrip()
		ratings = [x.text for x in soup.find("dd", class_="rating tags").find_all('a', class_="tag")]
		popular = self._popular( soup.find('dd', class_="hits").text )
		return language == 'English' and popular and "Explicit" not in ratings

	def _extract_meta(self):
		super()._extract_meta()
		soup = BeautifulSoup(self.get_request().content.decode('utf-8'), "html.parser")
		title = soup.find("h2", class_="title heading").text.rstrip().lstrip()
		author = soup.find("h3", class_="byline heading").text.rstrip().lstrip()
		text = [self._clean_text(chapter.text) for chapter in soup.find('div', id = "chapters").find_all('p')] # find_all('div', class_='userstuff'): separates by chapter instead of by paragraph
		return title, author, text

