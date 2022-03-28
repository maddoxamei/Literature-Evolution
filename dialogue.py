from pyspark.sql import SparkSession
# from pyspark import sparkContext
from text_functions import load_texts
from itertools import groupby
from numpy import diff, var
from functools import reduce

def conversation_length( text ):
	"""

	@return min conversation length, max conversation length, average conversation length, variance conversation length; for a given text
	@type (int, int, float, float)
	"""
	annotation = [i for i, paragraph in enumerate(text) if '"' in paragraph]
	if annotation == []:
		return 0, 0, 0.0, 0.0
	conversation_lengths = [len(list(g))+1 for k, g in groupby(diff(annotation)==1) if k]
	if conversation_lengths == []:
		return 1, 1, 1.0, 0.0
	return min(conversation_lengths), max(conversation_lengths), sum(conversation_lengths)/len(conversation_lengths), var(conversation_lengths)


def extract_dialogue( paragraph ):
	"""

	@return length of an entire dialogue sequence, the number of segments composing the dialogue sequence, word-to-segment ratio, dialogue flag, 1 (used to calculate total # of paragraphs)
	@type (int, int, float, int, int)
	"""
	dialogue_segments = [len(dialogue.split()) for dialogue in paragraph.split('"')[1::2]]
	total_words = sum(dialogue_segments)
	segments = len(dialogue_segments)
	return total_words, segments, total_words/segments if segments > 0 else 0, int(segments > 0), 1


def dialogue_stats( text ):
	"""

	@return average dialogue length, average number of dialogue segments, average word-to-segment ratio, proportion of dialogue containing paragraphs
	@type (float, float, float, float)
	"""
	stats = list(map(extract_dialogue, filter(lambda x: '"' in x, text)))
	if stats == []:
		return 0.0, 0.0, 0.0
	if len(stats) == 1:
		return stats[0]
	info = reduce( lambda x, y: (x[0]+y[0], x[1]+y[1], x[2]+y[2], x[3]+y[3], x[4]+y[4]), stats )
	return info[0]/info[3], info[1]/info[3], info[2]/info[3], info[3]/info[4]

	spark = SparkSession.builder.getOrCreate()
	info = spark.sparkContext.parallelize( text ).filter(lambda x: '"' in x).map( extract_dialogue ).reduce( lambda x, y: x[0]+y[0], x[1]+y[1], x[2]+y[2], x[3]+y[3], x[4]+y[4] )
	return info[0]/info[3], info[1]/info[3], info[2]/info[3], info[3]/info[4]

def main():
	"""

	@return list of conversation_length return objects and dialogue_stats return objects for each text object of each text type
	@type (list, list)
	"""
	books, fanfics = load_texts()
	stats_books = list(map( lambda x: conversation_length(x.text) + dialogue_stats(x.text), books ))
	stats_fanfiction = list(map( lambda x: conversation_length(x.text) + dialogue_stats(x.text), fanfics ))
	return stats_books, stats_fanfiction

	spark = SparkSession.builder.getOrCreate()
	stats_books = spark.sparkContext.parallelize( books ).map( lambda x: conversation_length(x.text) + dialogue_stats(x.text) ).collect()
	stats_fanfiction = spark.sparkContext.parallelize( fanfics ).map( lambda x: conversation_length(x.text) + dialogue_stats(x.text) ).collect()
	return stats_books, stats_fanfiction

if __name__ == '__main__':
	main()
