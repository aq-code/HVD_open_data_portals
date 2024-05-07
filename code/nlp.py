import operator 
from collections import OrderedDict

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

#import nltk
#nltk.download('stopwords')

def tokenizer(categories: list[str]) -> list[str]:
    """
    returns a list of lower case tokens from a list of categories, example:
    for a list of categories containing ["Public Safety", "Economic Development"] the method returns:
    ["public", "safety", "economic", "development"]

    params:
        categories:  list of strings to tokenize

    return:
        a list of strings
    """
    tokens = []
    for category in categories:
        tokens.extend([token.lower() for token in word_tokenize(category)])
        
    return tokens

def remove_stop_words(tokens: list[str], additional_remove: list[str]) -> list[str]:
    """
    removes the stop words available on the nltk corpus stop words list and the additional tokens passed as parameter.

    params:
        tokens:  list of strings to be filtered
        additional_remove: list of strings to filter alongside the nltk corpus stop words list.

    return:
        list of filtered strings 
    """
    return [token for token in tokens if token not in stopwords.words("english") and token not in additional_remove]

def count_word_frequency(lstWords):
    
    dictWordFreq = {}
    for word in lstWords:
        freq = dictWordFreq.get(word)
        if freq is None:
            freq = 0
        freq += 1
        dictWordFreq.update({word : freq})
    
    return OrderedDict(sorted(dictWordFreq.items(),
                            key = operator.itemgetter(1),
                            reverse = True))