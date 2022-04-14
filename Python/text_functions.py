from text_objects import Book, FanFiction
import pickle

def _scrape_books(number_of_texts = 0, book_ids = [], min_book_popularity = 0, **kwargs):
	"""
	Generate a corpus of "valid" books from the Project Gutenberg website.

	A valid book is an English text (not audio book) that is categorized as Literature and meets a minimum popularity (based on downloads in the last 30 days) or rank, if specified.
	Validation does NOT occur for any book whose id is specified for inclusion in the corpus.

	All id-specified books are included in the corpus, regardless of corpus size constraints; they are added first
	Should more books need to be added, random books are scraped until the corpus size constraints are met.

    Examples:		code --> return
		_scrape_books()			-->		[]
		_scrape_books(number_of_texts = 3)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, min_book_popularity = 600)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, rank = 1000)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, book_ids = [2701])		-->		[Book, Book, Book]
		_scrape_books(book_ids = [2701])			-->		[Book]

	kwargs:
		@param max_text_id: the highest index in the Project Gutenberg collection to consider when randomly selecting a book. 
							Indexation is chronologically based on when the book is added to the collection.
		@type: int
		@param min_rank: require that a book be in the top <min_rank> books based on number of downloads in the last 30 days in descending order for inclusion in the corpus
		@type: int [1, infinity)

	@param: number_of_texts: required size of the corpus (units are in Book objects)
	@type: int
	@param: book_ids: 
	@type: list(int)
	@param: min_book_popularity: minimum number of downloads in the last 30 days that a book must have for inclusion in the corpus
	@type: int [0, infinity)
	@return the books which are to be included in the corpus
	@type: list(Book)
	"""
	books = [Book( text_id = idx ) for idx in book_ids]
	more = max( number_of_texts - len(books), 0 )
	books.extend(Book( min_popular = min_book_popularity, **kwargs ) for x in range(more))
	return books

def _scrape_fanfictions(number_of_texts = 0, fanfiction_ids = [], min_fanfiction_popularity = 0, **kwargs):
	"""
	Generate a corpus of "valid" fanfictions from the Archieve of Our Own (AOO) website.

	A valid fanfiction is an English, non-Explicit text which meets a minimum popularity (based on hits) or rank, if specified.
	Validation does NOT occur for any fanfiction whose id is specified for inclusion in the corpus.

	All id-specified books are included in the corpus, regardless of corpus size constraints; they are added first
	Should more books need to be added, random books are scraped until the corpus size constraints are met.

    Examples:		code --> return
		_scrape_books()			-->		[]
		_scrape_books(number_of_texts = 3)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, min_book_popularity = 600)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, rank = 1000)		-->		[Book, Book, Book]
		_scrape_books(number_of_texts = 3, book_ids = [2701])		-->		[Book, Book, Book]
		_scrape_books(book_ids = [2701])			-->		[Book]

	kwargs:
		@param max_text_id: the highest index in the AOO collection to consider when randomly selecting a fanfiction. 
							Indexation is not continuous, and therefore takes time to find a valid fanfiction - especially as the default is system max
		@type: int
		@param min_rank: require that a fanfiction be in the top <min_rank> fanfictions based on number of hits in descending order for inclusion in the corpus.
							This is the fastest method of semi-random selection.
		@type: int

	@param: number_of_texts: required size of the corpus (units are in FanFiction objects)
	@type: int
	@param: book_ids: 
	@type: list(int)
	@param: min_fanfiction_popularity: minimum number of hits that a fanfiction must have for inclusion in the corpus.
										This is an extremely taxing method for random selection. The suggested method is to use min_rank.
	@type: int
	@return the fanfictions which are to be included in the corpus
	@type: list(Book)
	"""
	fanfics = [FanFiction( text_id = idx ) for idx in fanfiction_ids]
	more = max( number_of_texts - len(fanfics), 0 )
	fanfics.extend(FanFiction( min_popular = min_fanfiction_popularity, **kwargs ) for x in range(more))
	return fanfics

def scrape_texts(*args, serialize = True, **kwargs):
	"""
	Generate three serialized corpus files: one for books hosted on Project Gutenberg website, 
													one for fanfictions hosted on Archive of Our Own, 
													and one as an aggregation of the previous two.

        Manual Overrides:
                1) number_of_texts < length of id array: does not randomly generate any texts, DOES collect all specified ids
                2) length of book id array != length of fanfiction array: Ignores disproportionate lengths and collects all specified ids

	Examples:		code --> return
		scrape_texts(number_of_texts = 3)		-->		 ([Book, Book, Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172])		-->		 ([Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(number_of_texts = 1, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172])		-->		 ([Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(): ([], [])

	args:
		none, as all parameters in the _scrape_books and _scrape_fanfictions functions have defaults and are therefore optional
	kwargs:
		see the parameters and kwargs of the _scrape_books and _scrape_fanfictions functions

	@param: serialize: a flag indicating whether the generated corpuses should be saved to local disc, overwritting any previously existing corpuses
	@type: bool
	"""
	books = _scrape_books(*args, **kwargs)
	if serialize:
		with open('corpus_books.pkl', 'wb') as file:
			pickle.dump(books, file)

	fanfics = _scrape_fanfictions(*args, **kwargs)
	if serialize:
		with open('corpus_fanfics.pkl', 'wb') as file:
			pickle.dump(fanfics, file)

	if serialize:
		with open('corpus.pkl', 'wb') as file:
			pickle.dump(books, file)
			pickle.dump(fanfics, file)
	return books, fanfics

def load_texts():
	"""
	Load the serialized corpus file from disk.
	Corpus file contains an aggregation of books hosted on Project Gutenberg website and fanfictions hosted on Archive of Our Own.

	Example:
		books, fanfics = load_texts()

	@return: two lists of texts belonging in the corpus: one for books and one for fanfictions
	@type: tuple
	"""
	with open('corpus.pkl', 'rb') as file:
		books = pickle.load(file)
		fanfics = pickle.load(file)
	return books, fanfics

def main():
	"""
	A wrapper function to facilitate random corpus generation of 10 books and fanfictions each (as required by the project assignment).
	Each text is within the top 1000 for their respective popularity metrics.
	"""
	scrape_texts(10, min_rank = 1000)

if __name__ == '__main__':
	books, fanfics = scrape_texts(1, serialize = False, min_rank = 1000)
