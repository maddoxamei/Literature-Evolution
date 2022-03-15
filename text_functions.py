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

        Manual Overrides:
                1) number_of_texts < length of id array: does not randomly generate any texts, DOES collect all specified ids
                2) length of book id array != length of fanfiction array: Ignores disproportionate lengths and collects all specified ids

	Examples:
		scrape_texts(number_of_texts = 3): ([Book, Book, Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(number_of_texts = 3, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172]): ([Book, Book, Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172]): ([Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(number_of_texts = 1, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172]): ([Book], [FanFiction, FanFiction, FanFiction])
		scrape_texts(): ([], [])
	"""
	books = _scrape_books(*args, **kwargs)
	fanfics = _scrape_fanfiction(*args, **kwargs)
	if serialize:
		with open('corpus.pkl', 'wb') as file:
			pickle.dump(books, file)
			pickle.dump(fanfics, file)
	return books, fanfics

def load_texts():
	"""

	Examples:
		books, fanfics = load_texts()
	"""
	with open('corpus.pkl', 'rb') as file:
		books = pickle.load(file)
		fanfics = pickle.load(file)
	return books, fanfics

def main():
	scrape_Texts(10)

if __name__ == '__main__':
	books, fanfics = scrape_Texts(3, book_ids = [2701], fanfiction_ids = [37116025, 37601341, 37602172])