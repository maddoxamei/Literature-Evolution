import requests, random, sys, os
import pandas as pd
import pickle
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import Counter

from text_objects import Book, FanFiction
from text_functions import scrape_texts,load_texts,main

import pyspark
from pyspark.sql import SparkSession
sc = pyspark.SparkContext("local[*]", "Sample Context")

import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('large_grammars')

#Not Used
#from nltk.parse import RecursiveDescentParser
#grammar = nltk.data.load('grammars/large_grammars/atis.cfg')
#rd = RecursiveDescentParser(grammar)

def obj_to_string_list(book):
    #Same method now works with books and fanfiction.
    return(book.text)

def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    #https://datagy.io/python-replace-item-in-list/
    #I gather this is faster than doing a for loop.
    return [item_to_replace_with if item == item_to_replace else item for item in list_to_replace]
    
def convert_to_part_of_speech(sentence):
    #Input: sentence as string
    #Output: List of complex part of speech tokens
    tokens = nltk.word_tokenize(sentence)
    
    #This line can be used to replace quotation symbols with another symbol before processing
    #tokens = replace_values(replace_values(tokens,"``","_"),"''","_")

    tagged = nltk.pos_tag(tokens)
    output = list(map(lambda x:x[1],tagged))
    return(output)

def add_proportions(rdd):
    #Input:An RDD of key/value pairs as tuples 
    #Output: RDD of key/value/proportion tuples
    rddTotal = rdd.map(lambda x:x[1])
    total = rddTotal.reduce(lambda x,y:x+y)
    return(rdd.map(lambda x:(x[0],x[1],x[1]/total)))

def isWord(tpl):
    if(tpl[0]=="''" or tpl[0]=="``"):
        return(False)
    if(len(tpl[0])>1):
        return(True)

def isPunctuation(tpl):
    if(tpl[0]=="''" or tpl[0]=="``"):
        return(True)
    if(len(tpl[0])==1):
        return(True)       
    
def isWordList(lst):
    return(list(filter(lambda x:len(x)>1 or x=="''" or x=="``",lst)))
    #return(list(filter(lambda x:len(x)>1,lst)))

def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    #https://datagy.io/python-replace-item-in-list/
    return [item_to_replace_with if item == item_to_replace else item for item in list_to_replace]
        
def POS_prop(bookText):
    #Input: Text of a book or fanfiction, with each sentence as a list of strings
    #Output: rdd containing count/proportion of all parts of speech.  [0] is all, [1] is words only, [2] is punctuation only.
    
    #Converts sentence list to summary count of POS (words+punctuation)
    rdd = sc.parallelize(bookText)
    rdd = rdd.map(convert_to_part_of_speech)
    rdd = rdd.map(Counter)
    rdd = rdd.map(lambda x:list(x.items())) #Convert from dictionary to list of tuples
    rdd = rdd.flatMap(lambda x:x)
    rdd = rdd.reduceByKey(lambda x, y: int(x) + int(y))
    rdd = add_proportions(rdd)
    
    #Words only
    rddWords = rdd.filter(isWord)
    rddWords = add_proportions(rddWords)

    #Punctuation Only
    rddPunctuation = rdd.filter(isPunctuation)
    rddPunctuation = add_proportions(rddPunctuation)

    return((rdd,rddWords,rddPunctuation))
    
def replace_with_simple(lstPOS):
    j = -1
    for i in lstPOS:
        j+=1
        if i=='NN' or i=='NNP' or i=='NNPS' or i=='NNS' or i=='PRP' or i=='WP':
            lstPOS[j]='Noun'
        elif i=='VB' or i=='VBD' or i=='VBG' or i=='VBN' or i=='VBP' or i=='VBZ' or i=='MD':
            lstPOS[j]='Verb'
        elif i=='JJ' or i=='JJR' or i=='JJS' or i=='POS' or i=='PRP$':
            lstPOS[j]='Adj'
        elif i=='RB' or i=='RBR' or i=='RBS' or i=='WRB':
            lstPOS[j]='Adv'
        else: #POS not listed above are dropped
            lstPOS[j]=''
    
    lstPOS = list(filter(lambda x:x!='',lstPOS)) #Remove blank entries
    return(lstPOS)

def sentence_structure(bookText, bSimple, bWordOnly):
    #Input: Text of a book or fanfiction, with each sentence as a list of strings
    #Output: rdd of all complex sentence structures appearing, along with their count

    rdd = sc.parallelize(bookText)
    rdd = rdd.map(convert_to_part_of_speech)
    
    if bWordOnly:
        rdd = rdd.map(isWordList)
    if bSimple:
        rdd = rdd.map(replace_with_simple)
    
    rdd = rdd.map(lambda x:(tuple(x),1)) #tupe() is so we can use x as a key
    rdd = rdd.reduceByKey(lambda x, y: int(x) + int(y))
    rdd = add_proportions(rdd)
    return(rdd)


def combine_as_dataframe(dfFull,rdd,strTitle,strAuthor,strType):
    rdd = rdd.map(lambda x:(strType,strAuthor,strTitle,x[0],x[1],x[2]))
    df = pd.DataFrame(list(rdd.collect()), columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])
    df = pd.concat([dfFull,df])
    return(df)

def summarize_by_lit_type(dfFull):
    #Converts result dataframe to a combined summary of books and fanfiction.
    #Input: Detailed result dataframe
    #Output: Summary dataframe
    dfFull = dfFull.drop(['author','title'],axis=1)
    #Split
    dfBook = dfFull[dfFull['lit_type']=='Book']
    dfBook = dfBook.groupby(['lit_type','var_placeholder']).sum()
    
    dfFanfic = dfFull[dfFull['lit_type']=='Fanfiction']
    dfFanfic = dfFanfic.groupby(['lit_type','var_placeholder']).sum()
    
    #Get totals
    intTotalBook = sum(dfBook['count'])
    intTotalFanfic = sum(dfFanfic['count'])   
    
    #Get Proportions
    dfBook['proportion'] = dfBook['count'].apply(lambda x:x/intTotalBook)
    dfFanfic['proportion'] = dfFanfic['count'].apply(lambda x:x/intTotalFanfic)
    #Recombine
    dfFull = pd.concat([dfBook,dfFanfic])
    return(dfFull)
    
    
lstPOSTypes = [('JJ',0),('JJR',0),('JJS',0),('POS',0),
             ('PRP$',0),('RB',0),('RBR',0),('RBS',0),
             ('WRB',0),('CC',0),('DT',0),('PDT',0),('UH',0)
             ,('NN',0),('NNP',0),('NNPS',0),('NNS',0),('IN',0)
             ,('PRP',0),('WP',0),('MD',0),('VB',0),('VBD',0),
             ('VBG',0),('VBN',0),('VBP',0),('VBZ',0),('CD',0),
             ('EX',0),('FW',0),('LS',0),('RP',0),('TO',0),('WDT',0)]

# ###TEST CODE###
str1 = "Have a heart that never hardens, and a temper that never tires, and a touch that never hurts"
str2 = "I loved her against reason, against promise, against peace, against hope, against happiness, against all discouragement that could be."
str3 = "To begin my life with the beginning of my life, I record that I was born (as I have been informed and believe) on a Friday, at twelve o'clock at night."
lstTest1 = [str1,str2,str3]
str1 = "The quick brown fox jumped over the lazy dog."
str2 = "The red brown dog hopped under the happy fox."
str3 = "The quite brown fox jumped over the incensed dog."
lstTest2 = [str1,str2,str3]


###Driver Code###

#Import Corpus
#filename = 'home\tfitzgerald\idc5131\corpus_books.pkl'
filename_books = 'corpus_books.pkl'
filename_fanfiction = 'corpus_fanfictions.pkl'
corpus = (pickle.load(open(filename_books,'rb')),pickle.load(open(filename_fanfiction,'rb')))

dfPOS_all = pd.DataFrame(columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])
dfPOS_words = pd.DataFrame(columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])
dfPOS_punc = pd.DataFrame(columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])
dfComplex_SS = pd.DataFrame(columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])
dfSimple_SS = pd.DataFrame(columns = ['lit_type', 'author', 'title','var_placeholder','count','proportion'])

#Run functions on corpus
for literature_type in range(2):
    for book in corpus[literature_type]:
        #Basic information
        strTitle = book.title
        strAuthor = book.author
        if str(type(book)).find('Book') >= 0:
            strType = 'Book'
        else:
            strType = 'Fanfiction'
        #print(strTitle,strAuthor,strType)

        #Text Operations
        lstText = obj_to_string_list(book)
        #print(lstText[0:5])

        #Part of Speech
        POS_Results = POS_prop(lstText)
        rddPOS_Results_Full = POS_Results[0]
        rddPOS_Results_Word_Only = POS_Results[1]
        rddPOS_Results_Punc_Only = POS_Results[2]

        dfPOS_all = combine_as_dataframe(dfPOS_all,rddPOS_Results_Full,strTitle,strAuthor,strType)
        dfPOS_words = combine_as_dataframe(dfPOS_words,rddPOS_Results_Word_Only,strTitle,strAuthor,strType)
        dfPOS_punc = combine_as_dataframe(dfPOS_punc,rddPOS_Results_Punc_Only,strTitle,strAuthor,strType)

        #Complex Sentence Structure
        rddComplexStructure = sentence_structure(lstText,False,True)
        dfComplex_SS = combine_as_dataframe(dfComplex_SS,rddComplexStructure,strTitle,strAuthor,strType)
        #print(dfComplex_SS)

        #Simple Sentence Structure
        rddSimpleStructure = sentence_structure(lstText,True,True)
        dfSimple_SS = combine_as_dataframe(dfSimple_SS,rddSimpleStructure,strTitle,strAuthor,strType)
        #print(rddSimpleStructure.collect()[0])

    
    
#Finalize results for export
dfPOS_all_summary = summarize_by_lit_type(dfPOS_all)
dfPOS_words_summary = summarize_by_lit_type(dfPOS_words)
dfPOS_punc_summary = summarize_by_lit_type(dfPOS_punc)
dfComplex_SS_summary = summarize_by_lit_type(dfComplex_SS)
dfSimple_SS_summary = summarize_by_lit_type(dfSimple_SS)

lstResults = [dfPOS_all,dfPOS_words,dfPOS_punc,dfComplex_SS,dfSimple_SS]
lstResultsSummary = [dfPOS_all_summary,dfPOS_words_summary,dfPOS_punc_summary,dfComplex_SS_summary,dfSimple_SS_summary]
lstResultType = ['POS_all','POS_word','POS_punctuation','SS_complex','SS_simple']

# print(dfPOS_words_summary)
# print(dfPOS_punc_summary)

for i in range(len(lstResults)):
    lstResults[i] = lstResults[i].rename(columns={"var_placeholder": lstResultType[i]})
    lstResultsSummary[i] = lstResultsSummary[i].rename(columns={"var_placeholder": lstResultType[i]})
    lstResults[i].to_csv(lstResultType[i]+'.csv')
    lstResultsSummary[i].to_csv(lstResultType[i]+'_summary.csv')