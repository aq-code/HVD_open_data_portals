# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 17:16:18 2019

@author: HG
"""
import nltk

from nltk import word_tokenize, pos_tag

from wordnet import tagged_to_synset, synsets_similarity

import time

import logging
logging.basicConfig(filename='logging.log',level=logging.DEBUG)

#import nltk
#nltk.download('averaged_perceptron_tagger')

#import nltk
#nltk.download('wordnet')

#nltk.download('wordnet_ic')

import json
import portal
from portal import Portal
from portal import read_portals_from_json_file

def readPortalsFromJsonFile(portalsFile):
        
    lstPortals = []
    with open(portalsFile, 'r') as json_file:  
        data = json.load(json_file)
        for p in data:
            portal = Portal()
            portal.setCity(p["city"])
            portal.setUrl(p["url"])
            portal.setCoord(p["coord"])
            portal.setCategorization(p["categorization"])
            portal.setPlatform(p["platform"])
            portal.setCategories(p['categories'])
            lstPortals.append(portal)
    
    return lstPortals

def readCategoriesFromJsonFile(categoriesFile):
    
    lstCategories = []
    
    with open(categoriesFile, 'r') as json_file:  
        data = json.load(json_file)
        for p in data:
            lstCategories.append(p)
    
    return lstCategories


#calcula a similaridade entre duas sentenças, utilizando os seis métodos    
def sentence_similarity(sentence1, sentence2, first_synset=True):
    
    """ compute the sentence similarity using Wordnet """
    
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))

    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word, first_synset) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word, first_synset) for tagged_word in sentence2]

    # Filter out the Nones
    all_synsets1 = [ss for ss in synsets1 if ss]
    all_synsets2 = [ss for ss in synsets2 if ss]
    
    score1_path = 0.0
    score1_wup = 0.0
    score1_lch = 0.0
    score1_res = 0.0
    score1_jcn = 0.0
    score1_lin = 0.0
    count1 = 0
 
    it_all_synsets1 = iter(all_synsets1)
    
    # For each synsets of each word in the first sentence
    for synsets1 in it_all_synsets1:
        
        best_score_path = 0.0
        best_score_wup = 0.0 
        best_score_lch = 0.0
        best_score_res = 0.0
        best_score_jcn = 0.0
        best_score_lin = 0.0
        
        it_all_synsets2 = iter(all_synsets2)
        
        # For each synsets of each word in the second sentence
        # Get the similarity value of the most similar synset in the other sentence
        for synsets2 in it_all_synsets2:
            
            best_score_path, best_score_wup, best_score_lch, \
            best_score_res, best_score_jcn, best_score_lin = synsets_similarity(synsets1, synsets2)
            
            score1_path += best_score_path
            score1_wup += best_score_wup
            score1_lch += best_score_lch
            score1_res += best_score_res
            score1_jcn += best_score_jcn
            score1_lin += best_score_lin
        
            count1 += 1
 
    # Average the values
    if(score1_path != 0):
        score1_path /= count1
    
    if(score1_wup != 0):
        score1_wup /= count1
        
    if(score1_lch != 0):
        score1_lch /= count1
        
    if(score1_res != 0):
        score1_res /= count1
    
    if(score1_jcn != 0):
        score1_jcn /= count1
        
    if(score1_lin != 0):
        score1_lin /= count1
        
    score2_path = 0.0 
    score2_wup = 0.0
    score2_lch = 0.0
    score2_res = 0.0
    score2_jcn = 0.0 
    score2_lin = 0.0
    count2 = 0    
       
    it_all_synsets2 = iter(all_synsets2)
    
    # For each word in the second sentence
    for synsets2 in it_all_synsets2:
        
        best_score_path = 0.0 
        best_score_wup = 0.0
        best_score_lch = 0.0
        best_score_res = 0.0
        best_score_jcn = 0.0 
        best_score_lin = 0.0
        
        it_all_synsets1 = iter(all_synsets1)
        
        # For each synsets of each word in the first sentence
        # Get the similarity value of the most similar synset in the other sentence
        for synsets1 in it_all_synsets1:
            
            best_score_path, best_score_wup, best_score_lch, \
            best_score_res, best_score_jcn, best_score_lin = synsets_similarity(synsets1, synsets2)          
            
            score2_path += best_score_path
            score2_wup += best_score_wup
            score2_lch += best_score_lch
            score2_res += best_score_res
            score2_jcn += best_score_jcn
            score2_lin += best_score_lin
        
            count2 += 1
 
    # Average the values
    if(score2_path != 0 ):
        score2_path /= count2
        
    if(score2_wup != 0 ):
        score2_wup /= count2
        
    if(score2_lch != 0 ):
        score2_lch /= count2
        
    if(score2_res != 0 ):
        score2_res /= count2
        
    if(score2_jcn != 0 ):
        score2_jcn /= count2
        
    if(score2_lin != 0 ):
        score2_lin /= count2
    
    score_path = (score1_path + score2_path) / 2
    score_wup = (score1_wup + score2_wup) / 2
    score_lch = (score1_lch + score2_lch) / 2
    score_res = (score1_res + score2_res) / 2
    score_jcn = (score1_jcn + score2_jcn) / 2
    score_lin = (score1_lin + score2_lin) / 2
    
    return score_path, score_wup, score_lch, score_res, score_jcn, score_lin

def get_lst_similarities(category, lstCategoriesToMatch):
    
    best_sim_path = 0.0 
    best_sim_wup = 0.0
    best_sim_lch = 0.0
    best_sim_res = 0.0
    best_sim_jcn = 0.0 
    best_sim_lin = 0.0
    
    best_category_path = ""
    best_category_wup = ""
    best_category_lch = ""
    best_category_res = ""
    best_category_jcn = ""
    best_category_lin = ""
        
    it_categories_to_match = iter(lstCategoriesToMatch)
    for category_coverage in it_categories_to_match:
        
        sim_path, sim_wup, sim_lch, \
        sim_res, sim_jcn, sim_lin = sentence_similarity(category, category_coverage)
        
        if sim_path > best_sim_path:
            best_sim_path = sim_path
            best_category_path = category_coverage
            
        if sim_wup > best_sim_wup:
            best_sim_wup = sim_wup
            best_category_wup = category_coverage
            
        if sim_lch > best_sim_lch:
            best_sim_lch = sim_lch
            best_category_lch = category_coverage
            
        if sim_res > best_sim_res:
            best_sim_res = sim_res
            best_category_res = category_coverage
            
        if sim_jcn > best_sim_jcn:
            best_sim_jcn = sim_jcn
            best_category_jcn = category_coverage
            
        if sim_lin > best_sim_lin:
            best_sim_lin = sim_lin
            best_category_lin = category_coverage
    
    lstSimilarities = []
    lstSimilarities.append("path"), lstSimilarities.append(best_sim_path), lstSimilarities.append(best_category_path)
    lstSimilarities.append("wup"), lstSimilarities.append(best_sim_wup), lstSimilarities.append(best_category_wup)
    lstSimilarities.append("lch"), lstSimilarities.append(best_sim_lch), lstSimilarities.append(best_category_lch)
    lstSimilarities.append("res"), lstSimilarities.append(best_sim_res), lstSimilarities.append(best_category_res)
    lstSimilarities.append("jcn"), lstSimilarities.append(best_sim_jcn), lstSimilarities.append(best_category_jcn)
    lstSimilarities.append("lin"), lstSimilarities.append(best_sim_lin), lstSimilarities.append(best_category_lin)
    
    return lstSimilarities

from collections import OrderedDict
import operator 
import random

def get_most_elected_category(lst_similarities):

    dictCategoryFreq = {}
    
    best_category_path = lst_similarities[2]
    best_category_wup = lst_similarities[5]
    best_category_lch = lst_similarities[8]
    best_category_res = lst_similarities[11]
    best_category_jcn = lst_similarities[14]
    best_category_lin = lst_similarities[17]
    
    freq = dictCategoryFreq.get(best_category_path)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_path : freq} )
    
    freq = dictCategoryFreq.get(best_category_wup)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_wup : freq} )
    
    freq = dictCategoryFreq.get(best_category_lch)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_lch : freq} )
    
    freq = dictCategoryFreq.get(best_category_res)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_res : freq} )
    
    freq = dictCategoryFreq.get(best_category_jcn)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_jcn : freq} )
    
    freq = dictCategoryFreq.get(best_category_lin)
    if(freq is None):
        freq = 0
    freq += 1
    dictCategoryFreq.update( {best_category_lin : freq} )
    
    dictFreqOrd = OrderedDict(sorted(dictCategoryFreq.items(),
                                     key = operator.itemgetter(1),
                                     reverse = True))

    maxFreq = max(dictFreqOrd.values())
    
    best_categories = []
    for best_category, freq in dictFreqOrd.items():
        if (freq == maxFreq):     
            best_categories.append(best_category)

    if len(best_categories) > 1:
        index = random.randint(0, len(best_categories) - 1)
        return best_categories[index]
    
    return best_categories[0]
            
    
def fillDictCategoriesMatch(categories, lstCategoriesToMatch):
    
    dictCategorySimilarities = {}
    dictCategoryMatch = {}
    
    it_categories = iter(categories)
    for category in it_categories:
        
        lst_similarities = get_lst_similarities(category, lstCategoriesToMatch) 
        dictCategorySimilarities.update( {category : lst_similarities} )
        
        best_category = get_most_elected_category(lst_similarities)
        dictCategoryMatch.update( {category : best_category} )
 
    return dictCategorySimilarities, dictCategoryMatch 

def fillDictPortalsCategoryMatch(lstPortal, lstCategoriesCoverage):
    
    dictPortalsCategoryMatch = {}
    dictPortalsCategorySimilarities = {}

    it_portals = iter(lstPortal)
    for portal in it_portals:

        # AQ: 05042024 mods
        #categories = portal.getCategories()
        categories = portal.categories
        dictCategorySimilarities, dictCategoryMatch = fillDictCategoriesMatch(categories, lstCategoriesCoverage)
        # AQ: 05042024 mods
        #dictPortalsCategorySimilarities.update( {portal.getCity() : dictCategorySimilarities} )
        #dictPortalsCategoryMatch.update( { portal.getCity() : dictCategoryMatch} )
        dictPortalsCategorySimilarities.update({portal.city: dictCategorySimilarities})
        dictPortalsCategoryMatch.update({portal.city: dictCategoryMatch})

    return dictPortalsCategoryMatch, dictPortalsCategorySimilarities

def write_categories_match(dictPortalsCategoryMatch, dictPortalsCategorySimilarities, similarityFile, categoryMatchFile ):
    
    file = open(similarityFile, 'w')
    s = json.dumps(list(dictPortalsCategorySimilarities.items()), 
                   indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
    file.writelines(s)
    file.close()
    
    file = open(categoryMatchFile, 'w')
    s = json.dumps(list(dictPortalsCategoryMatch.items()), 
                   indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
    file.writelines(s)
    file.close()

def test(first_synset = True):
    # Testing the code
    sentence1 = 'Public Safety'
    sentence2 = 'Safety'

    import time 
    start = time.time()
     
    sim_path, sim_wup, sim_lch, \
    sim_res, sim_jcn, sim_lin = sentence_similarity(sentence1, sentence2, first_synset)
    
    print("path sim: {:.2f}".format(sim_path))
    print("wup sim:  {:.2f}".format(sim_wup))
    print("lch sim:  {:.2f}".format(sim_lch))
    print("res sim:  {:.2f}".format(sim_res))
    print("jcn sim:  {:.2e}".format(sim_jcn))
    print("lin sim:  {:.2f}".format(sim_lin))
    
    end = time.time()
    
    print("\n")
    time = (end - start)
    print('duracao: {:.2f}'.format(time) + " s")




#if __name__ == '__main__':

def compute_Alignment(output_dir):
    import time

    #####output_dir = "output/"

    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    portalsFile = output_dir + 'portals_category_usage.json'
    categoriesFile = output_dir + 'most_coverage_categories.json'
    similarityFile = output_dir + 'portals_category_similarities_100_cities_all_synsets.json'
    categoryMatchFile = output_dir + 'portals_category_match_100_cities_all_synsets.json'

    ## AQ: mod 04042024 - Error on readPortalsFromJsonFile -
    lstPortal = portal.read_portals_from_json_file(portalsFile)

    print("Number of Portals: " + "{0}".format(len(lstPortal)))

    lstCategoriesCoverage = readCategoriesFromJsonFile(categoriesFile)
    print("Number of Best Coverage Categories: " + "{0}".format(len(lstCategoriesCoverage)))
    print("\n")

    start = time.time()

    dictPortalsCategoryMatch, dictPortalsCategorySimilarities = fillDictPortalsCategoryMatch(lstPortal, lstCategoriesCoverage)
    write_categories_match(dictPortalsCategoryMatch, dictPortalsCategorySimilarities, similarityFile, categoryMatchFile)

    end = time.time()

    print("\n")
    time = (end - start)
    print('Duration: {:.2f}'.format(time) + " s")