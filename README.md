# Literature-Evolution
Comparison of classic literature to modern fan fiction

Subfolders
    Python - This contains all of our data extraction/processing files.
    static - This contains output data and images used in the presentation.
    R - This contains .rmd files that went into our presentation.
    Other - Anything not in the above 3 folders was probably used for the bookdown.  Besides this readme, of course.

Python
    .py files
        These include the data scrape & spark processing.

        text_objects.py - Randomly or specifically (via id) obtain a text from Project Gutenberg and Archieve of Our Own via web text-scraping
            - If random, validation occurs to make sure it is an acceptable text (i.e. not explicit, meets a minimum popularity quota, etc.)
            - Text cleaning and meta data extraction occurs if the text passes validation
        text_functions.py - Functions to obtain texts based on passed id's, quotas, and other params
        words.py - This returns word frequencies & frequency comparisons between books and fanfiction.
        dialogue.py - This takes book/fanfic text, and returns statistics on dialogue (both single-person and dialogue sequences).
        utils.py - Takes books/fanfics objects as input.  Returns word frequencies, from each category and comparative.
        structure_functions.py - This takes corpus.pkl as input and returns statistics on POS & sentence structure as a series of .csv files.
        csv_creation.py - This generates the .csv's used for the word clouds.  Not the original copy.

Static

    .pkl files
        This is the corpus that made up our sample.
        
        corpus.pkl - Both books and fanfiction objects.
        corpus_books.pkl - Just the books.
        corpus_fanfiction.pkl - Just the fanfiction.

    .png files
        These were used for the presentation.

    .csv files
        This is what we imported into R for analysis.  All (except sample_notes) were generated from python code.
        
        1.csv - Word frequency data for classic literature.
        2.csv - Word frequency data for modern fanfiction.
        fanfics.csv - Dialogue and conversation data for each individual book/fanfiction.
        POS_all.csv - POS frequency, grouped by lit type and title.  Words & Punctuation.
        POS_punctuation.csv - Punctuation only.
        POS_words.csv - Words only.
        SS_simple.csv - Frequency of simplified sentence structure in each book.
            Output from nltk POS tagging fed into replace_with_simple function from structure_function.py.
        sample_notes.csv - Data for table explaining sample data in presentation.
        book_dialogue.csv - Dialogue data for classic literature.
        fanfic_dialogue.csv - Dialogue data for fanfiction.

.rmd files
	These are what went into the bookdown for the presentation.
	01-Introduction.rmd - Libraries used, .csv imports, brief text intro.
    02-text_acquisition.rmd - This describes the process we used to acquire our sample.
    03-corpus_overview.rmd - This is a brief, mostly subjective, overview of what our sample consisted of.
    04-Data_processing_method.rmd - This describes all the processing between data scraping and our final data.
    05-findings.rmd - This contains visualizations & some brief text analysis of our findings.