from pyspark.sql import SparkSession
from pyspark import sparkContext
import 

def conversation_length( text ):
	"""

	@return min conversation length, max conversation length, average conversation length, variance conversation length; for a given text
	@type (int, int, int, int)
	"""
	annotation = [i for i, paragraph in enumerate(text) if '"' in paragraph]
	conversation_lengths = [len(list(g))+1 for k, g in groupby(np.diff(annotation)==1) if k]
	return min(conversation_lengths), max(conversation_lengths), sum(conversation_lengths)/len(conversation_lengths), np.var(conversation_lengths)


def extract_dialogue( paragraph ):
	"""

	@return length of an entire dialogue sequence, the number of segments composing the dialogue sequence, 1 (used to calculate total # of paragraphs)
	@type (int, int, int)
	"""
	dialogue_segments = [len(dialogue.split()) for dialogue in paragraph.split('"')[1::2]]
	return sum(dialogue_segments), len(dialogue_segments), 1


def dialogue_stats( text ):
	"""

	@return average dialogue length, average number of dialogue segments
	@type (int, int)
	"""
	spark = SparkSession.builder.getOrCreate()
	info = spark.sparkContext.parallelize( text ).map( extract_dialogue ).reduce( lambda x, y: x[0]+y[0], x[1]+y[1], x[2]+y[2] )
	return info[0]/info[2], info[1]/info[2]

def main():
	books, fanfics = load_texts()
	spark = SparkSession.builder.getOrCreate()
	stats_books = spark.sparkContext.parallelize( books ).map( lambda x: conversation_lengths(x.text), dialogue_stats(x.text) )
	stats_fanfiction = spark.sparkContext.parallelize( fanfics ).map( lambda x: conversation_lengths(x.text), dialogue_stats(x.text) )
	print(stats_books.collect())
	print(stats_fanfiction.collect())

if __name__ == '__main__':
	main()