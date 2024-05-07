from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError

import logging
logging.basicConfig(filename='logging.log',level=logging.DEBUG)

brown_ic = wordnet_ic.ic('ic-brown.dat')

class SynsetSimilarityInterface():
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        pass

class PathSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_path = synset1.path_similarity(synset2)
        except WordNetError as err:
            sim_path = 0.0
            logging.warning(err)
        return sim_path

class WupSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_wup = synset1.wup_similarity(synset2)
        except WordNetError as err:
            sim_wup = 0.0
            logging.warning(err)
        return sim_wup

class LchSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_lch = synset1.lch_similarity(synset2)
        except WordNetError as err:
            sim_lch = 0.0
            logging.warning(err)
        return sim_lch

class ResSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_res = synset1.res_similarity(synset2, brown_ic)
        except WordNetError as err:
            sim_res = 0.0
            logging.warning(err)
        return sim_res

class JcnSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_jcn = synset1.jcn_similarity(synset2, brown_ic)
        except WordNetError as err:
            sim_jcn = 0.0
            logging.warning(err)
        return sim_jcn

class LinSimilarity(SynsetSimilarityInterface):
    def calculate_similarity(synset1: wn.synset, synset2: wn.synset) -> float:
        try:
            sim_lin = synset1.lin_similarity(synset2, brown_ic)
        except WordNetError as err:
            sim_lin = 0.0
            logging.warning(err)
        return sim_lin

def penn_to_wn(tag: str) -> str: 
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    if tag.startswith('D'):
        return 'd'
    
    return None
    

def tagged_to_synset(word: str, tag: str, first_synset: bool = True) -> list[wn.synset]:
    """ Returns a list of wordnet synsets available for the word passed as parameter """
    """ If first_synset is true, returns only the first synset found for the word """     
    wn_tag = penn_to_wn(tag)
        
    if wn_tag is None:
        return None
     
    try:
        if(first_synset == True):
            synsets = []
            synsets.append((wn.synsets(word, wn_tag)[0]))
            return synsets
        else:
            return wn.synsets(word, wn_tag)
    except Exception as err:
        logging.warning(err)
        return None

def synset_similarity(synset1: wn.synset, synset2: wn.synset):
    """ Calculates different similarities between two synsets """
    
    sim_path = PathSimilarity.calculate_similarity(synset1, synset2)
    sim_wup = WupSimilarity.calculate_similarity(synset1, synset2)
    sim_lch = LchSimilarity.calculate_similarity(synset1, synset2)
    sim_res = ResSimilarity.calculate_similarity(synset1, synset2)
    sim_jcn = JcnSimilarity.calculate_similarity(synset1, synset2)
    sim_lin = JcnSimilarity.calculate_similarity(synset1, synset2)
        
    return sim_path, sim_wup, sim_lch, sim_res, sim_jcn, sim_lin

def synsets_similarity(synsets1, synsets2):

    ### calcula a maior similaridade entre os dois synsets  
    best_score_path = 0.0
    best_score_wup = 0.0
    best_score_lch = 0.0
    best_score_res = 0.0
    best_score_jcn = 0.0
    best_score_lin = 0.0
    
    it_synsets1 = iter(synsets1)
    
    # For each synset in the first synsets
    for synset1 in it_synsets1:
        
        it_synsets2 = iter(synsets2)
        
        for synset2 in it_synsets2:
            
            sim_path, sim_wup, sim_lch, \
            sim_res, sim_jcn, sim_lin = synset_similarity(synset1, synset2)
              
            if sim_path is None:
                sim_path = 0.0
                
            if sim_wup is None:
                sim_wup = 0.0
                
            if sim_lch is None:
                sim_lch = 0.0
                
            if sim_res is None:
                sim_res = 0.0
                    
            if sim_jcn is None:
                sim_jcn = 0.0
                
            if sim_lin is None:
                sim_lin = 0.0
                
            if sim_path > best_score_path:
                best_score_path = sim_path
                
            if sim_wup > best_score_wup:
                best_score_wup = sim_wup
                
            if sim_lch > best_score_lch:
                best_score_lch = sim_lch
            
            if sim_res > best_score_res:
                best_score_res = sim_res
                
            if sim_jcn > best_score_jcn:
                best_score_jcn = sim_jcn
                
            if sim_lin > best_score_lin:
                best_score_lin = sim_lin
                
    return best_score_path, best_score_wup, best_score_lch, best_score_res, best_score_jcn, best_score_lin