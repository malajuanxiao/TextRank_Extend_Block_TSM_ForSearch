#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:37:14 2019

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
        
        
normal_sum_list = []  
textrank_sum_list = []      
dis = 0



start = 0
end = 50
total_time = 0
qu_list = qu_list[start:end]
ex_dict = {}
with open("../ex/extend" + str(start)+"_"+str(end), "r", encoding='utf-8') as extend_object: #
    lines = list(extend_object.readlines())
    for line in lines:
        index = line[:-1].split(":")[0]
        ex_words_list = eval(line[:-1].split(":")[1])
        if isinstance(ex_words_list, dict):
            ex_dict[index] = ex_words_list  
        else:
            ex_dict[index] = {}

#print(ex_dict)





qu_size = 50
top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []
top_all_plist = []
top_all_rlist = []



docs_have = []  #存储所有查询对应的文档编号集合
for test_dict in qu_list:
    #预处理问题
    que_doc = Stem_qu(tokenize(test_dict['content']))
    inv_filename = "../04_group_tx_inv/normal/" + test_dict['index']
    
    deal_str_list = []
    inverted_word = {}
    doc_have = []
    for line in open(inv_filename,'r'): 
        deal_str = line[:-1].split(":")[0]
        deal_str_list = eval(line[:-1].split(":")[1])
        inverted_word[deal_str] = deal_str_list  
        
        
    for que_word in que_doc:
        if que_word in inverted_word:
            doc_have.extend(inverted_word[que_word])
      
    
    
    doc_have_list = list(set(doc_have))
    
    candi_sum = len(doc_have_list)
    normal_sum_list.append(candi_sum)
    
    
    docno_list = []
    rel_list = []
    origin_docs = []
    all_rela = 0
    with open("../04_groups/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
            
            if doc_data['doc_no'] in doc_have_list:
                origin_docs.append(doc_data['content'])
                rel_list.append(doc_data['r'])
                docno_list.append(doc_data['doc_no'])
            if doc_data['r'] != "0":
                all_rela += 1
    
    if len(origin_docs) - candi_sum != 0:
        print("error")
    #print(len(origin_docs),candi_sum)
        

        
    
    processed_raw_docs = [tokenize(doc) for doc in origin_docs]
    processed_docs = Stem_voca(processed_raw_docs)
    
    
    bm25Model = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    start = time.time()
    
    
    
    #获取普通结果
    score_dict = {}
    scores = bm25Model.get_scores(que_doc,average_idf)
    for idx,score_item in enumerate(scores):
        score_dict[idx] = score_item
    
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    
    end = time.time()
    total_time += (end - start)
    
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:5]):
        rel_str = str(rel_list[ int(score_item[0])])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    print(test_dict['index']," ",rela, " ",all_rela," " ,find_all, " ", (rela*1.0) / min(find_all,5))  
    top_5_plist.append((rela*1.0) / min(find_all,5))
    top_5_rlist.append((rela*1.0) / all_rela)
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:10]):
        rel_str = str(rel_list[ int(score_item[0])])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    top_10_plist.append((rela*1.0) / min(find_all,10))
    top_10_rlist.append((rela*1.0) / all_rela)
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:20]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
                
                
    top_20_plist.append((rela*1.0) / min(find_all,20))
    top_20_rlist.append((rela*1.0) / all_rela)
        
    
    
    find_all = len(score_list)
    rela = 0
    for i,score_item in enumerate(score_list):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
    
    top_all_plist.append((rela*1.0) / find_all)
    top_all_rlist.append((rela*1.0) / all_rela)
    
    



print(sum(top_5_plist)/qu_size)
print(sum(top_5_rlist)/qu_size)
print(sum(top_10_plist)/qu_size)
print(sum(top_10_rlist)/qu_size)
print(sum(top_20_plist)/qu_size)
print(sum(top_20_rlist)/qu_size)
print(sum(top_all_plist)/qu_size)
print(sum(top_all_rlist)/qu_size)

print("total_time:",total_time)
print("avg_time:",total_time/50)


total_time = 0
textrank_sum_list = []


#textrank+ex
qu_size = 50
top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []



top_all_plist = []
top_all_rlist = []

docs_have = []  #存储所有查询对应的文档编号集合
for idx,test_dict in enumerate(qu_list):
    #预处理问题
    que_doc = Stem_qu(tokenize(test_dict['content']))
    inv_filename = "../04_group_tx_inv/textrank_txbm/" + test_dict['index']
    
    
    
    deal_str_list = []
    inverted_word = {}
    for line in open(inv_filename,'r'): 
        deal_str = line[:-1].split(":")[0]
        deal_str_list = eval(line[:-1].split(":",1)[1])
        inverted_word[deal_str] = deal_str_list 
            
          
    start = time.time()
    score_dict = {}
    score_list = []
    for que_word in que_doc:
        if que_word in inverted_word:
            for doc_item in inverted_word[que_word]:
                doc_tu = doc_item.copy().popitem()
                doc_id = doc_tu[0]
                value = doc_tu[1]
                score = score_dict.setdefault(doc_id, 0) 
                score += value[1]
                '''
                if idx == 0 and doc_id == 'FBIS3-41158':
                    print(que_word,score, value[1])
                '''
                #score += value[0]*value[1]
                score_dict[doc_id] = score
    
    for ex_word,ex_factor in ex_dict[test_dict['index']].items():
        if ex_word in inverted_word:
            for doc_item in inverted_word[ex_word]:
                doc_tu = doc_item.copy().popitem()
                doc_id = doc_tu[0]
                value = doc_tu[1]
                score = score_dict.setdefault(doc_id, 0) 
                score += ex_factor*value[1]
                #score += ex_factor*value[0]*value[1]
                score_dict[doc_id] = score
    
    
    
    
    '''
    
    score_dict = {}
    score_list = []
    for que_word in que_doc:
        if que_word in inverted_word:
            #print(inverted_word[que_word])
            for doc_item in inverted_word[que_word].items():
                doc_id = doc_item[0]
                value = doc_item[1]
                score = score_dict.setdefault(doc_id, 0) 
                score += value
                #score += value[0]*value[1]
                score_dict[doc_id] = score
                
    for ex_word,ex_factor in ex_dict[test_dict['index']].items():
        if ex_word in inverted_word:
            for doc_item in inverted_word[ex_word].items():
                doc_id = doc_item[0]
                value = doc_item[1]
                score = score_dict.setdefault(doc_id, 0) 
                score += ex_factor*value
                #score += ex_factor*value[0]*value[1]
                score_dict[doc_id] = score
            
    '''  
    textrank_sum_list.append(len(score_dict))
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    
    
    end = time.time()
    total_time += end - start
    '''
    if idx == 0:
        print(score_list[:20])
    '''
    
    
    #print(score_list[:20])
    rel_dict = {}
    all_rela = 0
    with open("../04_groups/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
            rel_dict[doc_data['doc_no']] = doc_data['r']
            if doc_data['r'] != "0":
                all_rela += 1
    #print(rel_dict)
    
    
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:5]):
        rel_str = str(rel_dict[score_item[0]])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    print(test_dict['index']," ",rela, " ",all_rela," " ,find_all, " ", (rela*1.0) / min(find_all,5),len(score_list))  
    top_5_plist.append((rela*1.0) / min(find_all,5))
    top_5_rlist.append((rela*1.0) / all_rela)
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:10]):
        rel_str = str(rel_dict[score_item[0]])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    top_10_plist.append((rela*1.0) / min(find_all,10))
    top_10_rlist.append((rela*1.0) / all_rela)
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:20]):
        rel_str = str(rel_dict[score_item[0]])
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
                
                
    top_20_plist.append((rela*1.0) / min(find_all,20))
    top_20_rlist.append((rela*1.0) / all_rela)
        
    
    '''
    find_all = len(score_list)
    rela = 0
    for i,score_item in enumerate(score_list):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
        
    
    
    top_all_plist.append((rela*1.0) / find_all)
    top_all_rlist.append((rela*1.0) / all_rela)
    '''
print("total_time:",total_time)    
    

  
    

print(sum(top_5_plist)/qu_size)
print(sum(top_5_rlist)/qu_size)
print(sum(top_10_plist)/qu_size)
print(sum(top_10_rlist)/qu_size)
print(sum(top_20_plist)/qu_size)
print(sum(top_20_rlist)/qu_size)
print(sum(top_all_plist)/qu_size)
print(sum(top_all_rlist)/qu_size)


#print(len(normal_sum_list),len(textrank_sum_list))
'''
for i in range(len(textrank_sum_list)):
    dis += (normal_sum_list[i] - textrank_sum_list[i])
print("减少了:",dis)
'''



































