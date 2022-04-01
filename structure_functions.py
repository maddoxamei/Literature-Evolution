import requests, random, sys, os
import pandas as pd
import pickle
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import Counter

import pyspark
from pyspark.sql import SparkSession
sc = pyspark.SparkContext("local[*]", "Sample Context")

import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')


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
    
def isWord(tpl):
    if(len(tpl[0])>1):
        return(True)
def isPunctuation(tpl):
    if(len(tpl[0])==1):
        return(True)       
        
def POS_prop(bookText):
    #Input: Text of a book or fanfiction, with each sentence as a list of strings
    #Output: List containing proportion of total words each part of speech makes up.
    
    #Converts sentence list to summary count of POS (words+punctuation)
    rdd = sc.parallelize(bookText)
    rdd = rdd.map(convert_to_part_of_speech)
    rdd = rdd.map(Counter)
    rdd = rdd.map(lambda x:list(x.items())) #Convert from dictionary to list of tuples
    rdd = rdd.flatMap(lambda x:x)
    rdd = rdd.reduceByKey(lambda x, y: int(x) + int(y))
    
    #Words only
    rddWords = rdd.filter(isWord)
    rddWord_temp = rddWords.map(lambda x:x[1])
    totalWords = rddWord_temp.reduce(lambda x,y: x+y)

    #Punctuation Only
    rddPunctuation = rdd.filter(isPunctuation)
    rddPunc_temp = rddPunctuation.map(lambda x:x[1])
    totalPunctuation = rddPunc_temp.reduce(lambda x,y: x+y)

    #Proportions
    rddWordProp = rddWords.map(lambda x:(x[0],x[1]/totalWords))
    rddPunctuationProp = rddPunctuation.map(lambda x:(x[0],x[1]/totalPunctuation))
    
    lstOutput1 = rdd.collect()
    lstOutput2 = rddWordProp.collect()
    lstOutput3 = rddPunctuationProp.collect()
    return((lstOutput1,lstOutput2,lstOutput3))
    

###TEST CODE###
strTest = "Have a heart that never hardens, and a temper that never tires, and a touch that never hurts"
strTest2 = "I loved her against reason, against promise, against peace, against hope, against happiness, against all discouragement that could be."
strTest3 = "To begin my life with the beginning of my life, I record that I was born (as I have been informed and believe) on a Friday, at twelve o'clock at night. It was remarked that the clock began to strike, and I began to cry, simultaneously."
lstTest = [strTest,strTest2,strTest3]
#print(lstTest)


#POS_prop test
lstAnswer = POS_prop(lstTest)
print(lstAnswer[0])
print(lstAnswer[1])                                
print(lstAnswer[2])

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