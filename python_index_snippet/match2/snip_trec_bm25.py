#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 14:21:15 2019

@author: leyv
"""


# -*- coding: utf-8 -*-


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
    
    if len(snippet_score_list) >= 5 :
        snippet_score_list = snippet_score_list[:5]
    
    
    if ing_fun == 1:
        res_score = ( np.max(snippet_score_list) + np.average(snippet_score_list)) #* score_ratio
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

#print(len(raw_list))

#print(test_dict['index'])


idf = {}
with open("../support/trec_idf.txt", "r", encoding='utf-8') as record_object:
    lines = list(record_object.readlines())
    for line in lines:
        tmp_data = line.replace('\n','').split(" ")
        idf[tmp_data[0]] = float(tmp_data[1])








top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []
#qu_list = qu_list[:40]

pbar = tqdm(total = len(qu_list))
for test_dict in qu_list:
    pbar.update(1)
    #预处理问题
    qu_doc = Stem_qu(tokenize(test_dict['content']))
    score_list = []
    docno_list = []
    all_doc_slices =[]
    rel_list = []
    origin_docs = []
    all_rela = 0
    with open("../04_groups_02/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
            origin_docs.append(doc_data['content'])
            rel_list.append(doc_data['r'])
            docno_list.append(doc_data['doc_no'])
            if doc_data['r'] != "0":
                #print(doc_data['r'])
                all_rela += 1
                
    processed_docs = Stem_voca([tokenize(doc) for doc in origin_docs])
    all_doc_slices = Puncut(origin_docs)
    
    
    
    
    bm25Model = matchTool.Match(processed_docs,idf, [], 0)
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    
    #bm25Sim(self, qu_doc, doc_slice, doc_index,limit_ratio,filter_score)
    for doc_index,doc_slice in enumerate(all_doc_slices):
        #limit_ratio = (len(qu_doc) * 1.0 / (len(processed_docs[doc_index]) + 0.000001)   )*10
        sim_score_snippets,rel_snippet_ratio = bm25Model.bm25Sim(qu_doc, doc_slice, doc_index,0.1, average_idf)
        score = integScore(sim_score_snippets, rel_snippet_ratio,3)
        score_list.append((str(doc_index),score))
        
    
    '''
    #bm25Model = bm25.BM25(processed_docs,idf,3)
    score_dict = {}
    scores = bm25Model.get_scores_for_vn(qu_doc,average_idf)
    for idx,score_item in enumerate(scores):
        score_dict[idx] = score_item
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    '''
    score_list = sorted(score_list, key=lambda x:x[1],reverse=True)
    #score_list.sort(reverse=True) 
    
    
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:5]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_5_plist.append((rela*1.0) / min(find_all,5))
    top_5_rlist.append((rela*1.0) / all_rela)
        
    
    rela = 0
    for i,score_item in enumerate(score_list[:10]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_10_plist.append((rela*1.0) / min(find_all,10))
    top_10_rlist.append((rela*1.0) / all_rela)  
    
    
    rela = 0
    for i,score_item in enumerate(score_list[:20]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_20_plist.append((rela*1.0) / min(find_all,20))
    top_20_rlist.append((rela*1.0) / all_rela)  
    
pbar.close()       
'''
top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []
'''
print(top_5_plist[:10], top_5_rlist[:10], top_20_plist[:10], top_20_rlist[:10])

size = len(top_5_plist)
print(size)

print(sum(top_5_plist)/size)
print(sum(top_10_plist)/size)
print(sum(top_20_plist)/size)
print(sum(top_5_rlist)/size)
print(sum(top_10_rlist)/size)
print(sum(top_20_rlist)/size)




end = time.time()
print("程序运行时间:",end - start)









