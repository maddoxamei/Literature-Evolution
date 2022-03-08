from text_objects import Book, FanFiction

def _get_Books(number_of_texts, book_ids = [], **kwargs):
	books = [Book( text_id = idx ) for idx in book_ids]
	books.extend(Book() for x in range(number_of_texts - len(books)))
	return books

def _get_FanFiction(number_of_texts, fanfiction_ids = [], **kwargs):
	fanfics = [FanFiction( text_id = idx ) for idx in fanfiction_ids]
	fanfics.extend(FanFiction() for x in range(number_of_texts - len(fanfics)))
	return fanfics

def get_Texts(*args, **kwargs):
	"""

	Examples:
		get_Texts(3) - not recommended as searching for valid fanfiction can take a while
		get_Texts(3, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172])
	"""
	return _get_Books(*args, **kwargs), _get_FanFiction(*args, **kwargs)