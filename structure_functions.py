#This section is very incomplete.  convert_to_part_of_speech is about the only thing that works.


from text_objects import Book, FanFiction
from text_functions import scrape_texts
import pickle
import nltk
import pandas as pd
from collections import Counter

def pos_only(x):
    #Gets the part of speech after pos tagging.  
    return x[1]

def tuple_flipper(x):
    #Flips a tuple.
    return (x[1],x[0])

def convert_to_part_of_speech(sentence):
    #Input: sentence as string
    #Output: List of complex part of speech tokens
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    output = list(map(lambda x:x[1],tagged))  
    return(output)

def obj_to_string_list(book):
    #Only works with book currently.  Should also work with fanfiction.
    return(book[0].text)
    
def POS_prop(bookText):
    #*** THIS FUNCTIONS NEEDS A LOT OF SPARK CODE***
    #Input: Text of a book or fanfiction, with each sentence as a list of strings
    #Output: List containing proportion of total words each part of speech makes up.
    
    #Map to every element of Book.text/Fanfiction.text
    rdd = bookText
    #pos_list = rdd.map(convert_to_part_of_speech) #Spark
    pos_list = list(map(convert_to_part_of_speech,rdd)) #Python
    
    #Map these to all strings
    pos_count = Counter(pos_list) #Returns dictionary of key/value pairs
    pos_count_tuples = list(pos_count.items()) #converts above dictionary into a list of tuples
    print(pos_count_tuples)
    
    #Reduce by key on pos_count_tuples
    #Get sum of words
    #Convert reduce by key output to proportions
    #Sort proportion list
    #Return list of proportions
    print("Function not complete")    
    
    
#Get book/fanfiction
#test_run = scrape_texts(number_of_texts = 1)
test_run = scrape_texts(book_ids = [2701], fanfiction_ids = [37116025])



###TEST CODE###
#tplTest = ('Dog', 'NN')
#strTest = "Have a heart that never hardens, and a temper that never tires, and a touch that never hurts"
#strTest2 = "I loved her against reason, against promise, against peace, against hope, against happiness, against all discouragement that could be."
#strTest3 = "To begin my life with the beginning of my life, I record that I was born (as I have been informed and believe) on a Friday, at twelve o'clock at night. It was remarked that the clock began to strike, and I began to cry, simultaneously."
#lstTest = [strTest,strTest2,strTest3]

book_text = obj_to_string_list(test_run[0])
lstTest = book_text[750:753]
print(lstTest)

#Test for POS_prop
pos_list = list(map(convert_to_part_of_speech,lstTest))
print(pos_list)
pos_count = [Counter(pos_list[0]),Counter(pos_list[1]),Counter(pos_list[2])]
print(pos_count)



#Word+Part of speech as tuple
#tokens = nltk.word_tokenize(strTest)
#tagged = nltk.pos_tag(tokens)
#print(tagged)

#tagged = list(map(pos_only, tagged))
#tagged = list(map(tuple_flipper, tagged))
#print(tagged)

#print(convert_to_part_of_speech(strTest))

#pos_list = convert_to_part_of_speech(strTest)
###END TEST CODE###






def sentence_structure_complex_prop(bookText):
    #Input: Text of a book or fanfiction, with each sentence as a list of strings
    #Output: Dictionary of all complex sentence structures appearing, along with their count
    #Map to every element of Book.text/Fanfiction.text
    #pos_structure = convert_to_part_of_speech(sentence)
    print("Function not written")

def sentence_structure_simple_prop(bookText):
    #This will be same as complex version, but use simplified POS tagging (noun, verb, adj, etc. no punctuation)
    print("Function not written")    
        
###Paragraph Structure###
    #Average length of paragraph probably a good place to start.  Need list of paragraphs as input.