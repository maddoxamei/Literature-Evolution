# Literature-Evolution
Comparison of classic literature to modern fan fiction

.rmd files
	These are what went into the bookdown for the presentation.
	The files start with 01->05 indicating order.

.pkl files
	This is the corpus that made up our sample.
	
	corpus.pkl - Both books and fanfiction.
	corpus_books.pkl - Just the books.
	corpus_fanfiction.pkl - Just the fanfiction.

.py files
	These include the data scrape & spark processing.

	text_objects.py - 
	text_functions.py - 
	words.py - This returns word frequencies & frequency comparisons between books and fanfiction.
	dialogue.py - This returns statistics on dialogue.
	utils.py - 
	structure_functions.py - This takes corpus.pkl as input and returns statistics on POS & sentence structure as a series of .csv files.
	csv_creation.py - This generates the .csv's used for the word clouds.
	

    
/static
.png files
	These were used for the presentation.
.csv files
	This is what we imported into R for analysis.

	1.csv - 
	2.csv - 
	fanfics.csv - 
	POS_all.csv - POS frequency, grouped by lit type and title.  Words & Punctuation.
	POS_punctuation.csv - Punctuation only.
	POS_words.csv - Words only.
	SS_simple.csv - Frequency of simplified sentence structure in each book.
		Output from nltk POS tagging fed into replace_with_simple function from structure_function.py.
    sample_notes.csv - Data for table explaining sample data in presentation.
    book_dialogue.csv - Dialogue data for classic literature.
    fanfic_dialogue.csv - Dialogue data for