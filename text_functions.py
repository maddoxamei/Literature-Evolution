from text_objects import Book, FanFiction
import pickle

def _scrape_books(number_of_texts = 0, book_ids = [], min_book_popularity = 0, **kwargs):
	books = [Book( text_id = idx, min_popular = min_book_popularity ) for idx in book_ids]
	more = max( number_of_texts - len(books), 0 )
	books.extend(Book() for x in range(more))
	return books

def _scrape_fanfiction(number_of_texts = 0, fanfiction_ids = [], min_fanfiction_popularity = 0, **kwargs):
	fanfics = [FanFiction( text_id = idx, min_popular = min_fanfiction_popularity ) for idx in fanfiction_ids]
	more = max( number_of_texts - len(fanfics), 0 )
	fanfics.extend(FanFiction() for x in range(more))
	return fanfics

def scrape_texts(*args, serialize = True, **kwargs):
	"""

	Examples:
		get_Texts(3) - not recommended as searching for valid fanfiction can take a while
		get_Texts(3, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172])
	"""
	books = _scrape_books(*args, **kwargs)
	fanfics = _scrape_fanfiction(*args, **kwargs)
	if serialize:
		with open('corpus.pkl', 'wb') as file:
			pickle.dump(books, file)
			pickle.dump(fanfics, file)
	return books, fanfics

def load_texts():
	with open('corpus.pkl', 'rb') as file:
		books = pickle.load(file)
		fanfics = pickle.load(file)
	return books, fanfics
