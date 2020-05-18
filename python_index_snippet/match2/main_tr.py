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


qu_list = qu_list[0:50]


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
    normal_sum_list.append(candi_sum)
    if len(origin_docs) - candi_sum != 0:
        print("error")
    #print(len(origin_docs),candi_sum)
        

        
        
    processed_raw_docs = [tokenize(doc) for doc in origin_docs]
    processed_docs = Stem_voca(processed_raw_docs)
    
    bm25Model = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    
    
    
    
    #获取普通结果
    score_dict = {}
    scores = bm25Model.get_scores(que_doc,average_idf)
    for idx,score_item in enumerate(scores):
        score_dict[idx] = score_item
    
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:20]):
        rel_str = str(rel_list[ int(score_item[0])])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    print(rela, " ",all_rela," " ,find_all, " ", (rela*1.0) / min(find_all,20))  
    top_5_plist.append((rela*1.0) / min(find_all,20))
    top_5_rlist.append((rela*1.0) / all_rela)
        
    
    
    find_all = len(score_list)
    rela = 0
    for i,score_item in enumerate(score_list):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
    
    top_all_plist.append((rela*1.0) / find_all)
    top_all_rlist.append((rela*1.0) / all_rela)
    
    
    '''
    rela = 0
    for i,score_item in enumerate(score_list[:30]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_10_plist.append((rela*1.0) / min(find_all,30))
    top_10_rlist.append((rela*1.0) / all_rela)  
    
    
    rela = 0
    for i,score_item in enumerate(score_list[:50]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_20_plist.append((rela*1.0) / min(find_all,50))
    top_20_rlist.append((rela*1.0) / all_rela)
    '''
    
    
    




print(sum(top_5_plist)/qu_size)
print(sum(top_5_rlist)/qu_size)
print(sum(top_10_plist)/qu_size)
print(sum(top_10_rlist)/qu_size)
print(sum(top_all_plist)/qu_size)
print(sum(top_all_rlist)/qu_size)




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
    inv_filename = "../04_group_tx_inv/textrank/" + test_dict['index']
    
    
    doc_index_list = []
    inverted_word = {}
    doc_have = []
    for line in open(inv_filename,'r'): 
        deal_str = line[:-1].split(":")
        doc_index_list = eval(deal_str[1])
        for word in deal_str[0].split(" "):
            locations = inverted_word.setdefault(word, [])
            locations.extend(doc_index_list)
            
            
        
    for que_word in que_doc:
        if que_word in inverted_word:
            doc_have.extend(inverted_word[que_word])
            
            
    doc_have_list = list(set(doc_have))
    
    candi_sum = len(doc_have_list)
    '''
    if candi_sum < 30:
        print(doc_have_list)
    '''
    
    
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
    textrank_sum_list.append(candi_sum)
    if len(origin_docs) - candi_sum != 0:
        print("error")
    
    
    processed_raw_docs = [tokenize(doc) for doc in origin_docs]
    processed_docs = Stem_voca(processed_raw_docs)
    
    bm25Model = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    
    
    
    
    #获取普通结果
    score_dict = {}
    scores = bm25Model.get_scores(que_doc,average_idf)
    for idx,score_item in enumerate(scores):
        score_dict[idx] = score_item
    
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:20]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
    
    
    
    
    print(rela, " ",all_rela," " ,find_all, " ", (rela*1.0) / min(find_all,20))  
    top_5_plist.append((rela*1.0) / min(find_all,20))
    top_5_rlist.append((rela*1.0) / all_rela)
        
    
    
    find_all = len(score_list)
    rela = 0
    for i,score_item in enumerate(score_list):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
        
    
    
    top_all_plist.append((rela*1.0) / find_all)
    top_all_rlist.append((rela*1.0) / all_rela)
    
    
    

    '''
    rela = 0
    for i,score_item in enumerate(score_list[:30]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_10_plist.append((rela*1.0) / min(find_all,30))
    top_10_rlist.append((rela*1.0) / all_rela)  
    
    
    rela = 0
    for i,score_item in enumerate(score_list[:50]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_20_plist.append((rela*1.0) / min(find_all,50))
    top_20_rlist.append((rela*1.0) / all_rela)
    '''
    
    

print(sum(top_5_plist)/qu_size)
print(sum(top_5_rlist)/qu_size)
print(sum(top_10_plist)/qu_size)
print(sum(top_10_rlist)/qu_size)
print(sum(top_all_plist)/qu_size)
print(sum(top_all_rlist)/qu_size)



for i in range(len(textrank_sum_list)):
    dis += (normal_sum_list[i] - textrank_sum_list[i])
print(dis)










#
def FetchDocs_for_tr(self, c_data, que_docs,rel_docs):
    
    inv_filename = "../04_group_tx_inv/textrank/" + str(current_no)
    
    #获取倒排索引库
    inverted_word = {}
    for line in open(inv_filename,'r'): 
        deal_str = line[:-1].split(":")
        doc_index_list = eval(deal_str[1])
        for word in deal_str[0].split(" "):
            locations = inverted_word.setdefault(word, [])
            locations.extend(doc_index_list)
    
    docs_have = []  #存储所有查询对应的文档编号集合
    for idx,que_doc in enumerate(que_docs):
        doc_have = []
        for que_word in que_doc:
            if que_word in inverted_word:
                doc_have.extend(inverted_word[que_word])
                
        doc_have_list = list(set(doc_have))
        
        if len(doc_have_list) < 40:
            doc_have = doc_have + [i for i in range(40)]
            
        
        #doc_have = doc_have + [int(i)-1 for i in rel_docs[idx]]
        doc_have_list = list(set(doc_have))
        docs_have.append(doc_have_list)
    return docs_have








