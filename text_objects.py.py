import requests, random, sys, os
from bs4 import BeautifulSoup

_sep = str(os.linesep)
_max_book_id = 67577

code = requests.get("https://raw.githubusercontent.com/c-w/gutenberg/master/gutenberg/_domain_model/text.py").text
exec(code)

class Text():
	def __init__(self, max_text_id, text_url):
		 self.__max_text_id = max_text_id
		 self.__text_url = text_url
		 self.__text_id, self.__request = self.__find_text()

	def __validation(self, request):
		return True

	def __find_random_text(self):
		text_id = random.randint(1, self.__max_text_id)
		return text_id, requests.get( self.__text_url.format(id = text_id), allow_redirects=False )

	def __find_text(self):
		text_id, request = self.__find_random_text()
		while req.status_code != 200 and self.__validation(request):
			text_id, request = self.__find_random_text()
		return text_id, request

	def get_id(self):
		return self.__text_id

	def get_request(self):
		return self.__request


class Book(Text):
	def __init__(self):
		super().__init__(_max_book_id, 'https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt')

	def __validation(self, request):
		soup = BeautifulSoup(request.text, "html.parser")
		loc_class = soup.find('table', class_ = 'bibrec').find(property="dcterms:subject")
		if loc_class is None:
			return False
		language = soup.find(property="dcterms:language").find('td').text
		return language == True and 'literature' in loc_class.lower()

	def __populate(self):
		soup = BeautifulSoup(request.text, "html.parser")
		table = soup.find('table', class_ = 'bibrec')


		lines = .text.splitlines()

		# Isolates the book context from the header/footer information 
		idx_start = max(self.get_request().text.find(marker) for marker in TEXT_START_MARKERS) # request.text.upper().find("START OF THE PROJECT GUTENBERG EBOOK")
		idx_end = min(self.get_request().text.find(marker) for marker in TEXT_END_MARKERS if request.text.find(marker) > -1) # request.text.upper().find("END OF THE PROJECT GUTENBERG EBOOK")
		text = self.get_request().text[idx_start:idx_end].splitlines()[1:] # request.text[idx_start:idx_end].split("***", maxsplit = 1)[1]

		#soup.find('table', class_ = 'bibrec')

class Fanfiction(Text):
	def __init__(self):
		super().__init__(sys.maxsize, 'https://archiveofourown.org/works/{id}?view_full_work=true')
		self.title, self.author self.text = self.__extract_meta()

	def __validation(self, request):
		soup = BeautifulSoup(request.text, "html.parser")
		language = soup.find("dd", class_="language").text.rstrip().lstrip()
		ratings = [x.text for x in soup.find("dd", class_="rating tags").find_all('a', class_="tag")]
		return "Mature" not in ratings and language == 'English'

	def __extract_meta(self):
		soup = BeautifulSoup(self.get_request().text, "html.parser")
		title = soup.find("h2", class_="title heading").text.rstrip().lstrip()
		author = soup.find("h3", class_="byline heading").text.rstrip().lstrip()
		text = [chapter.text for chapter in soup.find('div', id = "chapters").find_all('p')] # find_all('div', class_='userstuff'): separates by chapter instead of by paragraph
		return title, author, text