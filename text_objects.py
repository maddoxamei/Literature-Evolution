import requests, random, sys, os
from bs4 import BeautifulSoup
from unidecode import unidecode
from pyspark.sql import SparkSession

_max_book_id = 67577

code = requests.get("https://raw.githubusercontent.com/c-w/gutenberg/master/gutenberg/_domain_model/text.py").text
exec(code)

class Text():
	"""
	kwargs:
		no kwargs parameters are used in this class, the existance of this parameter merely allows unused parameters to be specified
	
	@param max_text_id: the highest index in the online collection to consider when randomly selecting a text. 
	@type: int
	@param: text_url: website url to a specific text in the collection, with specification formatted for substitution
	@type: str
	@param: ranks_url: website url to the collection of texts sorted in descending order or popularity, with pagination formatted for substitution
	@type: str
	@param: ranks_text_class: html class name which indicates a text object on the <ranks_url> webpage; used for extracting all texts
	@type: str
	@param: text_id: a unique identification number used to reference a specific text in the collection
	@type: int [1, <max_text_id>)
	@param: min_popular: minimum popularity value (based on respective metric) that a text must for inclusion in the corpus
	@type: int [0, infinity)
	@param: min_rank: require that a book be in the top <min_rank> books based on the respective popularity metric for inclusion in the corpus
	@type: int [1, infinity)
	"""
	def __init__(self, max_text_id, text_url, ranks_url, ranks_text_class, text_id = None, min_popular = 0, min_rank = None, **kwargs):
		 self.__max_text_id = max_text_id
		 self.__text_url = text_url
		 self.__ranks_url = ranks_url 
		 self.__ranks_text_class = ranks_text_class
		 self.__text_id = text_id
		 self.__min_popular = min_popular
		 self.__min_rank = min_rank

	def _popular(self, popular_value):
		"""
		Comparison of a considered text's popularity (for respective metric) based on the established minimum requirement for inclusion in the corpus

		@param: considered text's popularity
		@type: int or numerical-only str
		@return: whether the considered text meets the popularity requirement
		@type: bool
		"""
		return int(popular_value) > self.__min_popular

	def _rank_pagination(self, rank):
		"""
		Calculates which page the <rank>th most popular validation-pending text appears in the <rank_url> collection; calculated page gets substituted into the <rank_url>

		@param: the relative popularity of a randomly selected, validation-pending text
		@type: int
		@return: the pagination number which the text appears on
		@type: int
		"""
		raise NotImplementedError

	def _rank_indexation(self, rank):
		"""
		Calculates where the <rank>th most popular validation-pending text appears in the list of texts on the <rank_url> webpage; 
		pagination has already occured to ensure the <rank>th text is in-fact listed on the specific page

		@param: the relative popularity of a randomly selected, validation-pending text
		@type: int
		@return: the relative location (index) which the specified text appears in on the webpage
		@type: int
		"""
		raise NotImplementedError

	def _validation(self, request):
		"""
		Ensures a selected text, based on randomly generated id or rank, is...
			actually contained in the online collection (no 404 error),
			written in English,
			satisfies the minimum popularity requirement,
			and satisfies the minimum rank requirement (if specified)
		Additional validation criteria are specific to the collection from which the text comes from; see child function for specifics.

		Validation does NOT occur for any book whose id is specified for inclusion in the corpus.

		@param: webpage of the text in question
		@type: requests.Response
		@return:
		@type: bool
		"""
		raise NotImplementedError

	def __find_random_text(self):
		"""
		Selects a text based on randomly generated id or rank (if specified)

		@return:
		@type: 
		"""
		if self.__min_rank is None:
			text_id = random.randint(1, self.__max_text_id)
		else:
			rank = random.randint(1, self.__min_rank)
			text_id = BeautifulSoup(requests.get(self.__ranks_url.format(self._rank_pagination(rank))).text, 'html.parser').find_all('li', class_= self.__ranks_text_class)[self._rank_indexation(rank)].find('a').get('href').split('/')[-1]
			text_id = int(text_id)			
		return text_id, requests.get( self.__text_url.format(id = text_id), allow_redirects=False )

	def __find_text(self):
		"""
		@return:
		@type:
		"""
		if self.__text_id is not None:
			return self.__text_id, requests.get( self.__text_url.format(id = self.__text_id) )
		text_id, request = self.__find_random_text()
		while not self._validation(request):
			text_id, request = self.__find_random_text()
			print( "Invalid text, finding another:", request.url )
		print( "Valid text:", request.url )
		return text_id, request

	def _clean_text(self, text):
		"""
		@param:
		@type:
		@return:
		@type:
		"""
		return unidecode( text.replace( os.linesep, ' ').strip() )

	def _clean_text_list(self, text_list):
		"""
		@param:
		@type:
		@return:
		@type:
		"""
		return [self._clean_text(paragraph) for paragraph in text_list if paragraph != '']
		return SparkSession.builder.getOrCreate().parallelize( text_list ).map( lambda paragraph: self._clean_text(paragraph) if paragraph != '' else None ).collect()

	def get_id(self):
		"""
		@return:
		@type:
		"""
		return self.__text_id

	def get_url(self):
		"""
		@return:
		@type:
		"""
		return self.__text_url.format(id = self.__text_id)

	def get_request(self):
		"""
		@return:
		@type:
		"""
		return self.__request

	def _extract_meta(self):
		"""
		@return:
		@type:
		"""
		self.__text_id, self.__request = self.__find_text()



class Book(Text):
	def __init__(self, **kwargs):
		""" 

		Examples: 
			Book()
			Book( text_id = 2701 )
			Book( min_popular = 10 )
		"""
		super().__init__(_max_book_id, "https://www.gutenberg.org/ebooks/{id}", 'https://www.gutenberg.org/ebooks/search/?query=&submit_search=Go!&start_index={}', 'booklink', **kwargs) #https://www.gutenberg.org/files/219/219-0.txt #'https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt'
		self.title, self.author, self.text = self._extract_meta()

	def _rank_pagination(self, rank):
		"""
		"""
		return rank

	def _rank_indexation(self, rank):
		"""
		"""
		return 0

	def _validation(self, request):
		"""
		Additional validation:
			is an English text (not audio book)
			is categorized as Literature
		"""
		if request.status_code != 200:
			return False
		soup = BeautifulSoup(request.text, "html.parser")
		loc_class = ['literature' in x.text.lower() for x in soup.find_all('tr', property="dcterms:subject")]
		language = soup.find(property="dcterms:language").find('td').text
		popular = self._popular( soup.find(itemprop = "interactionCount").text.split(maxsplit = 1)[0] )
		is_text = soup.find("table", class_ = "files").find_all('a', string = "Plain Text UTF-8")
		return is_text and language == 'English' and any(loc_class) and popular

	def _extract_meta(self):
		"""
		"""
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
		super().__init__(sys.maxsize, 'https://archiveofourown.org/works/{id}?view_full_work=true', 'https://archiveofourown.org/works/search?commit=Search&page={}&utf8=%E2%9C%93&work_search%5Bbookmarks_count%5D=&work_search%5Bcharacter_names%5D=&work_search%5Bcomments_count%5D=&work_search%5Bcomplete%5D=T&work_search%5Bcreators%5D=&work_search%5Bcrossover%5D=&work_search%5Bfandom_names%5D=&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Blanguage_id%5D=en&work_search%5Bquery%5D=&work_search%5Brating_ids%5D=&work_search%5Brelationship_names%5D=&work_search%5Brevised_at%5D=&work_search%5Bsingle_chapter%5D=0&work_search%5Bsort_column%5D=hits&work_search%5Bsort_direction%5D=desc&work_search%5Btitle%5D=&work_search%5Bword_count%5D=', 'work', **kwargs)
		self.title, self.author, self.text = self._extract_meta()

	def _rank_pagination(self, rank):
		"""
		"""
		return rank // 20 # int(rank/20)

	def _rank_indexation(self, rank):
		"""
		"""
		return rank % 20


	def _validation(self, request):
		"""
		Additional validation:
			is not rated as Explicit (Mature is allowed)
		"""
		if request.status_code != 200:
			return False
		soup = BeautifulSoup(request.text, "html.parser")
		language = soup.find("dd", class_="language").text.rstrip().lstrip()
		ratings = [x.text for x in soup.find("dd", class_="rating tags").find_all('a', class_="tag")]
		popular = self._popular( soup.find('dd', class_="hits").text )
		return language == 'English' and popular and "Explicit" not in ratings

	def _extract_meta(self):
		"""
		"""
		super()._extract_meta()
		soup = BeautifulSoup(self.get_request().content.decode('utf-8'), "html.parser")
		title = soup.find("h2", class_="title heading").text.rstrip().lstrip()
		author = soup.find("h3", class_="byline heading").text.rstrip().lstrip()
		text = [self._clean_text(chapter.text) for chapter in soup.find('div', id = "chapters").find_all('p')] # find_all('div', class_='userstuff'): separates by chapter instead of by paragraph
		return title, author, text

