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


def Puncut(processed_docs):
    all_doc_slices = []
    pattern = r'\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|\^|&|=|\+|，|。|、|；|‘|’|【|】|·|！|…|（|）'#|\(|\)|,'
    for text in processed_docs:
        sentence_list = re.split(pattern,text)
        for idx,sentence in enumerate(sentence_list):
            sentence_list[idx] = sentence.strip()
        raw_sentences = [tokenize(doc) for doc in sentence_list]
        sentence_list = Stem_voca(raw_sentences)
        sentence_list = list(filter(None, sentence_list))
        all_doc_slices.append(sentence_list)
    return all_doc_slices



def integScore(scores, score_ratio,ing_fun):
    res_score = 0
    snippet_score_list = [score[1] for score in scores]
    
    
    if len(snippet_score_list) == 0:
        return res_score
    snippet_score_list.sort(reverse=True) 
    '''
    if len(snippet_score_list) >= 5 :
        snippet_score_list = snippet_score_list[:5]
    '''
    
    if ing_fun == 1:
        res_score = ( np.max(snippet_score_list) + np.average(snippet_score_list)) * score_ratio
    elif ing_fun == 2:
        res_score = np.max(snippet_score_list) * score_ratio
    elif ing_fun == 3:
        rlen = len(snippet_score_list)
        weigth_whole = rlen*(rlen+1)/2
        
        s1 = 0
        for i in range(rlen):
            s1 += ((rlen-i)/weigth_whole * snippet_score_list[i])
        res_score = s1 #* score_ratio
    
    return res_score




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


#textrank+ex
qu_size = 50
top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []
total_time = 0


top_all_plist = []
top_all_rlist = []

docs_have = []  #存储所有查询对应的文档编号集合
Inf = 0
import math
for idx,test_dict in enumerate(qu_list):
    #预处理问题
    que_doc = Stem_qu(tokenize(test_dict['content']))
    inv_filename = "../04_group_tx_inv/textrank_txbm4/" + test_dict['index']
    
    
    
    deal_str_list = []
    inverted_word = {}
    for line in open(inv_filename,'r'): 
        deal_str = line[:-1].split(":")[0]
        deal_str_list = eval(line[:-1].split(":",1)[1])
        inverted_word[deal_str] = deal_str_list 
        
    
    
    
    
    
    
    #一次性装载
    max_score_list = []
    block_score_list = []
    can_sum = 0
    for que_word in que_doc:
        if que_word in inverted_word:
            for block_item in inverted_word[que_word]:
                max_score_list.append(block_item['max_score'])
                block_score_list.append(block_item['list'])
                can_sum += len(block_item['list'])
                
    
    for ex_word,ex_factor in ex_dict[test_dict['index']].items():
        if ex_word in inverted_word:
            for block_item in inverted_word[ex_word]:
                max_score_list.append(ex_factor*block_item['max_score'])
                block_score_list.append( [x*ex_factor for x in block_item['list']] )
                can_sum += len(block_item['list'])
    
    f_ratio = 0.2
    limit_block_num = math.ceil( f_ratio * len(max_score_list))
    limit_doc_num = f_ratio * can_sum
    
    start = time.time()            
    current_score_list = []  
    current_score_dict = {}
    
    #初始化
    k = 20
    m = len(max_score_list)
    n = 0
    next_score = 0
    temp_index = max_score_list.index(max(max_score_list))
    
    for i in range(len(max_score_list)):
        #逐步扫描
            
        
        temp_score_list = block_score_list[temp_index]
        #print(current_score,temp_score_list)
        max_score_list[temp_index] = Inf
        temp_index = max_score_list.index(max(max_score_list))
        next_score = max_score_list[temp_index]
        n = n+1
        #ob_flag = 0
        #operate
        
        for doc_item in temp_score_list:
            doc_id = doc_item[0]
            value = doc_item[1]
            score = current_score_dict.setdefault(doc_id, 0) 
            score += value
            current_score_dict[doc_id] = score
            
            
                
       
    current_score_list = sorted(current_score_dict.items(), key = lambda current_score_dict:current_score_dict[1],reverse=True)   
    
        
   

    
    
    
    end = time.time()
    total_time += (end-start)
    

    #print(score_list[0:3])

    textrank_sum_list.append(len(current_score_list))
    current_score_list = current_score_list[:20]
    
    
    #print(score_list)
    
    
    
    '''
    if idx == 0:
        print(score_list[:20])
    '''
    
    #print(score_list[:20])
    rel_dict = {}
    all_rela = 0
    
    origin_docs = []
    filter_docs = []
    origin_no_list = []
    filter_no_list = []
    
    all_doc_slices =[]
    
    with open("../04_groups/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
            origin_docs.append(doc_data['content'])
            origin_no_list.append(doc_data['doc_no'])
            rel_dict[doc_data['doc_no']] = doc_data['r']
            if doc_data['r'] != "0":
                all_rela += 1
    normal_sum_list.append(len(origin_no_list))
    
    
    
    
    for score_item in current_score_list:
        filter_no_list.append(score_item[0])
        doc_index = origin_no_list.index(score_item[0])
        filter_docs.append(origin_docs[doc_index])
        
    
    
    processed_docs = Stem_voca([tokenize(doc) for doc in filter_docs])
    all_doc_slices = Puncut(filter_docs)
    
    bm25Model = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    
    start = time.time() 
    temp_score_list = []
    for doc_index,doc_slice in enumerate(all_doc_slices):
        #limit_ratio = (len(qu_doc) * 1.0 / (len(processed_docs[doc_index]) + 0.000001)   )*10
        sim_score_snippets,rel_snippet_ratio = bm25Model.bm25Sim(que_doc, doc_slice, doc_index,0.45,4*average_idf)# average_idf)
        #print(rel_snippet_ratio)
        score = integScore(sim_score_snippets, rel_snippet_ratio,1)
        temp_score_list.append((str(filter_no_list[doc_index]),score))
    
    
    temp_score_list = sorted(temp_score_list, key=lambda x:x[1],reverse=True)
    #print(temp_score_list[:3])
    #print(filter_docs[:3])
    #print(rel_dict)
    
    end = time.time() 
    #total_time += (end-start)
    
    
    
    
    
    score_list = temp_score_list
    #score_list = current_score_list
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:5]):
        rel_str = str(rel_dict[score_item[0]])
        #print(rel_str)
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i+1
    print(test_dict['index']," ",rela, " ",all_rela," " ,find_all, " ", (rela*1.0) / min(find_all,5), len(score_list))  
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
    
    


    

print(sum(top_5_plist)/qu_size)
print(sum(top_5_rlist)/qu_size)
print(sum(top_10_plist)/qu_size)
print(sum(top_10_rlist)/qu_size)
print(sum(top_20_plist)/qu_size)
print(sum(top_20_rlist)/qu_size)
print(sum(top_all_plist)/qu_size)
print(sum(top_all_rlist)/qu_size)
avg_time = total_time/50
print(avg_time)
#print(len(normal_sum_list),len(textrank_sum_list))
'''
for i in range(len(textrank_sum_list)):
    dis += (normal_sum_list[i] - textrank_sum_list[i])
print("减少了:",dis)
'''

print("total_time:",total_time)
print("avg_time:",total_time/50)

































