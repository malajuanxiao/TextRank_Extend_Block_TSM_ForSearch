#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 00:43:24 2019

@author: leyv
"""
from nltk import stem
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
import re
from tqdm import tqdm
#import bm25_tool as bm25
import time
import matchTool
import numpy as np
import process as pp

start = time.time()



#去停用词
def tokenize(text):
    return [token for token in simple_preprocess(text) if token not in STOPWORDS]
#提取词根
def Stem_voca(processed_docs):
    WordNetStem = stem.WordNetLemmatizer()
    for idx,words in enumerate(processed_docs):
        for i,word in enumerate(words):
            words[i] = WordNetStem.lemmatize(word,"n")
        for i,word in enumerate(words):
            words[i] = WordNetStem.lemmatize(word,"v")
        #processed_docs[idx] = words
        processed_docs[idx] = [token for token in words if token not in STOPWORDS]
    return processed_docs


def Stem_qu(qu_doc):
    WordNetStem = stem.WordNetLemmatizer()
    for i,word in enumerate(qu_doc):
        qu_doc[i] = WordNetStem.lemmatize(word,"n")
    for i,word in enumerate(qu_doc):
        qu_doc[i] = WordNetStem.lemmatize(word,"v")
    #processed_docs[idx] = words
    qu_doc = [token for token in qu_doc if token not in STOPWORDS]
    return qu_doc


def select_words(deal_list , set_n):
    counter_dict = {}
    ex_set = set()
    for item in deal_list:
        counter_dict[item] = counter_dict.get(item,0) + 1
        if counter_dict[item] >= set_n:
            ex_set.add(item)
            
    return list(ex_set)

filename = '../trec/04数据集/04.testset'
file = open(filename)
qu_set = str(file.read())
file.close()
raw_list = qu_set.split('</top>')
num_r = re.compile(r'Number:(.*)\n')
title_r = re.compile(r'<title>(\n?)([\d\D]*)\n<desc>')
desc_r = re.compile(r'<desc>(\n?)([\d\D]*)\n<narr>')
narr_r = re.compile(r'<narr>(\n?)([\d\D]*)')


qu_list = []
for raw_item in raw_list[:-1]:
    qu_dict = {}
    #print(raw_item)
    num_object = re.search(num_r, raw_item)# num_r.match(raw_item)
    qu_dict['index'] = num_object.group(1).strip()
    
    title_object = re.search(title_r, raw_item)
    qu_dict['title'] = title_object.group(2).replace('\n',' ').strip()
    
    desc_object = re.search(desc_r, raw_item)
    qu_dict['desc'] = desc_object.group(2).replace('Description:','').replace('\n',' ').strip()
    
    narr_object = re.search(narr_r, raw_item)
    qu_dict['narr'] = narr_object.group(2).replace('Narrative:','').replace('\n',' ').strip()
    qu_dict['content'] =  qu_dict['title'] + '. ' + qu_dict['desc'] + '. ' + qu_dict['narr'].split(". ")[0] + '.'
    
    qu_list.append(qu_dict)

qu_size = len(qu_list)
print("查询条数:", qu_size)

idf = {}
with open("../support/trec_idf.txt", "r", encoding='utf-8') as record_object:
    lines = list(record_object.readlines())
    for line in lines:
        tmp_data = line.replace('\n','').split(" ")
        idf[tmp_data[0]] = float(tmp_data[1])



ex_word_dict = {}
start = 200
end = 250
for test_dict in qu_list[start:end]:
    #预处理问题
    ex_words = []
    que_doc = Stem_qu(tokenize(test_dict['content']))
    print(que_doc)
    
    
    documents = []
    
    with open("../04_groups/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
                
            if doc_data['r'] != "0":
                documents.append(doc_data['content'])
                
                
    
    preprocess = pp.PreProc(list(que_doc),documents)
    que_docs,processed_docs = preprocess.Normal()
    
    
    ma = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(ma.idf[k]), ma.idf.keys())) / len(ma.idf.keys())

    extend_word = ma.ewGen_occ_trec(que_doc,preprocess.corpus_words,documents,0.5,0.3)
    #ex_words = select_words(ex_words , 2)
    #print(test_dict['index']," extend words:",ex_words)
    print("finish:", test_dict['index'])
    ex_word_dict[test_dict['index']] = extend_word

#print(ex_word_dict)

with open("../ex/extend_conf"+str(start)+"_"+str(end) , "w", encoding='utf-8') as extend_object:
    for index,dict_item in ex_word_dict.items():
        extend_object.write(str(index)+':'+str(dict_item) + "\n")
        

            
        

end = time.time()


