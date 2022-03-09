from functools import reduce
from re import search


def counter(object_, tracked_elements = None, elements_contain = '', flags = 0):
	"""
	Count the frequencies/occurances of an object within a given itterable object

	@param: object_: an object of elements which to count the frequencies of
	@type: itterable object
	@param: tracked_elements: only count the frequecies of elements contained in this object, ignore all other elements
	@type: itterable object
	@param elements_contain: a regex pattern/expression an element must contain in order to be counted
	@type: str
	@param: flags: 
	@type: <enum 'RegexFlag'>

	Examples:		Code 	-->		Output

		String:					counter('Hello, World!')	-->		{'o': 2, 'W': 1, ',': 1, ' ': 1, 'd': 1, 'l': 3, 'e': 1, '!': 1, 'r': 1, 'H': 1}
								counter('Hello, World!', string.punctuation)	-->		{',': 1, '!': 1}

		List of words:			counter(['Hello', 'World', 'Hello', 'sad', 'Human'])	-->		{'sad': 1, 'Human': 1, 'World': 1, 'Hello': 2}
								counter(['Hello', 'World', 'Hello', 'sad', 'Human'], ['Hello','Human'])		-->		{'Human': 1, 'Hello': 2}
								counter(['Hello', 'World', 'Hello', 'sad', 'Human'], elements_contain = '^.{5}$')	-->		{'Human': 1, 'World': 1, 'Hello': 2}

		List of sentences: 		counter(['Hello, World!', 'Hello, World!', 'Hello sad Human'])		-->		{'Hello sad Human': 1, 'Hello, World!': 2}
								counter(['Hello, World!', 'Hello sad Human', 'Sad human world'], elements_contain = 'E', flags = re.IGNORECASE)		-->		{'Hello sad Human': 1, 'Hello, World!': 1}

								counter(['Hello, World!', 'Hello sad Human', 'Sad human world'], elements_contain = r'''(^\w{5}) # match 5-letter word at the start
           																			.+(N$) # must end in n ''', flags = re.IGNORECASE|re.VERBOSE)		-->		{'Hello sad Human': 1}
	"""
	if tracked_elements is None:
		return {o : object_.count(o) for o in set(object_) if search(elements_contain, o, flags)}
	return {o : object_.count(o) for o in set(object_)  if o in tracked_elements and search(elements_contain, o, flags)}


def havok_method(list_of_dictionaries):
	"""
	Code Credits: This function was obtained from Stack Overflow
		https://stackoverflow.com/questions/10461531/merge-and-sum-of-two-dictionaries


	@param: list_of_dictionaries: a list of dictionaries
	@type: [dict]

	Examples:
		havok_method([counter(''.join(book.text), string.ascii_letters), counter(''.join(book.text), string.punctuation)])
	"""
	def reducer(accumulator, element):
		for key, value in element.items():
			accumulator[key] = accumulator.get(key, 0) + value
		return accumulator
	return reduce(reducer, list_of_dictionaries, {})