def main():
	"""
	@return: book word frequencies, fanfiction word frequencies, word frequencies books and fanfics have in common, book word frequencies not in fanfiction, fanfiction word frequences not in books
	"""
	books, fanfics = load_texts()
	stats_books = sc.parallelize( books ).flatMap( lambda x: x.text ).flatMap( lambda x: [w.translate(str.maketrans('','',string.punctuation)) for w in x.lower().split()] ).map( lambda x: (x, 1) ).reduceByKey( lambda x, y: x + y )
	stats_fanfiction = sc.parallelize( fanfics ).flatMap( lambda x: x.text ).flatMap( lambda x: [w.translate(str.maketrans('','',string.punctuation)) for w in x.lower().split()] ).map( lambda x: (x, 1) ).reduceByKey( lambda x, y: x + y )
	return stats_books, stats_fanfiction, stats_books.intersection(stats_fanfiction), stats_books.subtract(stats_fanfiction), stats_fanfiction.subtract(stats_books)