# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 15:29:11 2019

@author: HG
"""

import os
import json
import operator 
from collections import OrderedDict

from nlp import tokenizer, remove_stop_words, count_word_frequency
from portal import read_portals_from_json_file, all_categories, exclude_portals_without_category
        
def count_portals_for_words(dictWordFreq, portals):

    words_to_remove = ["?","&","gis","/","kc","fy","foia","geo","city","data","go",
                         "-",",","houston","use","public","department","."]
    dictWordPortals = {}
       
    for word, freq in dictWordFreq.items():
        
        for portal in portals:
    
            tokens = tokenizer(portal.categories)
            words = remove_stop_words(tokens, words_to_remove)
    
            if word in words:
        
                lstPortals = dictWordPortals.get(word)
                if(lstPortals is None):
                    lstPortals = []
                      
                lstPortals.append(portal)
                    
                dictWordPortals.update( {word : lstPortals} )
                     
    return dictWordPortals
    
def fillDictWordPortalsDifference(dictWordPortals):
        
    dictWordPortalsDifference = {}
    previousPortals = []

    for word, portals in dictWordPortals.items():
    
        differentPortals = list( set(portals) - set(previousPortals) )  
        dictWordPortalsDifference.update( {word : differentPortals} )
    
        for portal in portals:
            previousPortals.append(portal)
                
    return dictWordPortalsDifference

def fillDictPortalsCoverage(dictWordFreq, portals):
        
    dictPortalsCoverage = {}
        
    dictWordPortals = count_portals_for_words(dictWordFreq, portals)
    dictWordPortalsDifference = fillDictWordPortalsDifference(dictWordPortals)
        
    portalWithCategories = exclude_portals_without_category(portals)
    
    somaPerc = 0
    for word, portais in dictWordPortalsDifference.items():
        perc = (len(portais) * 100 / len(portalWithCategories))
        somaPerc = somaPerc + perc
            
        dictPortalsCoverage.update({word : somaPerc})
        
    return dictPortalsCoverage

def more_Coverage_Words(dictAbrangenciaPortais, threshold):
    
    more_coverage_words = []
    
    for word, abrangencia in dictAbrangenciaPortais.items():
        
        if abrangencia < threshold:
            
            more_coverage_words.append(word)
        
        elif abrangencia == threshold:  
            
            more_coverage_words.append(word)
            return more_coverage_words
        
        elif abrangencia > threshold:
            
            return more_coverage_words
            
    return more_coverage_words

def fillDictWordCategoryFreq(more_coverage_words, portals, words_to_remove):
        
    dictWordCategoryFreq = {}
    for word in more_coverage_words:
                        
        dictFreq = {}
        for portal in portals:
            
            categories = portal.categories
            for category in categories:
                lst = []
                lst.append(category)
                tokens = tokenizer(lst)
                words = remove_stop_words(tokens, words_to_remove)
                
                if word in words:
                    freq = dictFreq.get(category)
                    if freq is None:
                        freq = 0
                    freq += 1
                    dictFreq.update( {category : freq} )
        dictFreqOrd = OrderedDict(sorted(dictFreq.items(),
                                         key = operator.itemgetter(1),
                                         reverse = True))            
        dictWordCategoryFreq.update( {word : dictFreqOrd} )  
    
    return dictWordCategoryFreq    

def fillDictWordFrequentlyCategories(dictTarget):
        
    dictWordFrequentlyCategories = {}       
    for target, dictFreq in dictTarget.items():
            
        maiorFreq = 0
        for categoria, freqB in dictFreq.items():
                        
            if freqB > maiorFreq:
                maiorFreq = freqB
            
        lstCategorias = []            
        for categoria, freqB in dictFreq.items():
                
            if(freqB == maiorFreq):
                lstCategorias.append(categoria)

        ### AQ: BEGIN 01022024 Check if more categories with the same frequency
        if len(lstCategorias) > 1:
            lstCategorias=select_most_repr_category(lstCategorias, dictFreq)
        ### AQ: END 01022024 Check if more categories with the same frequency

        dictWordFrequentlyCategories.update({target : lstCategorias})
    
    return dictWordFrequentlyCategories


### AQ 2024:  BEGIN - Deal with 'sibling' categories (with same max frequency) for words

def list_cities():
    portals_file = "../portals.json"
    portals = read_portals_from_json_file(portals_file)
    it_portals = iter(portals)
    cities=[]
    for portal in it_portals:
        cities.append(portal.city)
    return cities

def findWholeWord(w):
    import re
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def list_subset(lstCategorias):
    stopwords=['of','&','and',"-",",","'s"]
    new_list = [remove_stop_words(x.split(), stopwords) for x in lstCategorias]
    new_list.sort(key=lambda x: len(x), reverse=False)
    for e in new_list[1:]:
        if set(new_list[0]).issubset(set(e)):
            f = True
        else:
            return None
    return new_list[0]

def select_most_repr_category(lstCategorias,dictFreq):
    catmax=0
    stopwords=['of','&','and',"-",",","'s"]
    cities=list_cities()
    supercategory=list_subset(lstCategorias)
    if supercategory:
        return supercategory      ### if false return [maxcategory]
    for category in lstCategorias:
        countwords=0
        for catwords in remove_stop_words(category.split(),stopwords):
            if catwords in cities:
                countwords=0
                break
            else:
                for target, catFreq in dictFreq.items():
                    if category !=target:
                        if findWholeWord(catwords)(target):
                            countwords+=1
        if countwords>catmax:
           maxcategory=category
           catmax=countwords
    return [maxcategory]


def skimDoublesCategories(dictWordFrequentlyCategories):
    import json
    with open(dictWordFrequentlyCategories) as f:
        lstCategories = json.load(f)
        print(lstCategories)
    #listWordFrequentlyCategories = list(dictWordFrequentlyCategories.values())
    stopwords=['of','&','and',"-",",","'s"]
    new_list = [[x,remove_stop_words(x.split(), stopwords)] for x in lstCategories]
    new_list.sort(key=lambda x: len(x[0]), reverse=True)
    slist=[]
    found = False
    for i in range(0,len(new_list)):
        #new_list[:]=[x for x in new_list[i+1:] if not set(e[1]).issubset(set(x[1]))]
        #l = [x for x in new_list[i + 1:] if set(e[1]).issubset(set(x[1]))]
        e=new_list[i]
        for j in range(i+1,len(new_list)):
            s=new_list[j]
            if set(s[1]).issubset(set(e[1])):
                found=True
                break
        if found:
           found=False
        else:
            slist.append(e)
    slist.sort(key=lambda x: len(x[1]), reverse=False)
    print(slist)
    tmp=[x[0] for x in slist]
    tmp=[x for x in lstCategories if x in tmp]
    tmp=list(dict.fromkeys(tmp))
    with open(dictWordFrequentlyCategories,"w") as f:
        s = json.dumps(tmp, indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
        f.writelines(s)
        f.close()
    return tmp

### AQ END

def get_categories_from_dict_word_frequently(dictWordFrequentlyCategories):
    
    categories_lst = []
    for frequently_word, categories in dictWordFrequentlyCategories.items():
        
        for categorie in categories:
            categories_lst.append(categorie)
    
    return categories_lst
        

def write_categories(dictWordFrequentlyCategories, outputCategoriesFile):
    
    categories_lst = get_categories_from_dict_word_frequently(dictWordFrequentlyCategories)
    
    file = open(outputCategoriesFile, 'w')
    
    s = json.dumps(categories_lst, indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
    
    file.writelines(s)
    file.close()


def compute_Comprehensive_Set():
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("\n")

    portals_file = "../portals.json"
    categories_output_file = output_dir + 'most_coverage_categories.json'

    test=True
    if test:
        portals = read_portals_from_json_file(portals_file)

        print("Number of Portals: " + "{0}".format(len(portals)))

        lstCategories = all_categories(portals)
        print("Number of Categories: " + "{0}".format(len(lstCategories)))

        tokens = tokenizer(lstCategories)
        print("Number of tokens in categories: " + "{0}".format(len(tokens)))

        # AQ 09042024 ad  "?" (for Los Angeles)
        # words_to_remove = ["&","gis","/","kc","fy","foia","geo","city","data","go",
        #                      "-",",","houston","use","public","department","."]
        words_to_remove = ["?","&","gis","/","kc","fy","foia","geo","city","data","go",
                             "-",",","houston","use","public","department","."]

        words = remove_stop_words(tokens, words_to_remove)

        dictWordFreq = count_word_frequency(words)
        print("Number of words in categories: " + "{0}".format(len(dictWordFreq)))
        print("\n")
        print(dictWordFreq)
        print("\n")

        dictPortalsCoverage = fillDictPortalsCoverage(dictWordFreq, portals)
        print(dictPortalsCoverage)
        print("\n")

        trheshold = 99.0

        more_coverage_words = more_Coverage_Words(dictPortalsCoverage, trheshold)
        print(more_coverage_words)
        print("\n")

        dictWordCategoryFreq = fillDictWordCategoryFreq(more_coverage_words, portals, words_to_remove)
        print(dictWordCategoryFreq)
        print("\n")

        dictWordFrequentlyCategories = fillDictWordFrequentlyCategories(dictWordCategoryFreq)
        write_categories(dictWordFrequentlyCategories, categories_output_file)
        print(dictWordFrequentlyCategories)
    listWordFrequentlyCategories=[]
    listWordFrequentlyCategories=skimDoublesCategories(categories_output_file)
    print("End skimming: ",listWordFrequentlyCategories)
   # write_categories(dictWordFrequentlyCategories, categories_output_file)
    #print(dictWordFrequentlyCategories)
    print("\n")

