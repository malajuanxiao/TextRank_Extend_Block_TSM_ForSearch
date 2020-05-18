#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 18:07:56 2019

@author: leyv
"""


from nltk import stem
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.summarization import summarize
from gensim.summarization import keywords
import math




def change(text_str):
    continue_str = ""
    for str_item in text_str:
        continue_str += (str_item + " ")
    return continue_str[:-1] + "."
    

def tokenize(text):
    return [token for token in simple_preprocess(text.lower()) if token not in STOPWORDS]


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


def word_split(documents):
    processed_raw_docs = [tokenize(doc) for doc in documents]
    processed_docs = Stem_voca(processed_raw_docs)
    return processed_docs


def select_words(deal_list, set_n):
    counter_dict = {}
    ex_set = set()
    for item in deal_list:
        counter_dict[item] = counter_dict.get(item,0) + 1
        if counter_dict[item] >= set_n:
            ex_set.add(item)
    return list(ex_set)



PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25
    


def get_score(word, tf, idf, doc_len, avgdl, average_idf):
    idf = idf[word] if (word in idf and idf[word] >= 0) else EPSILON * average_idf
    score = idf * tf * (PARAM_K1 + 1)/ (tf + PARAM_K1 * (1 - PARAM_B + PARAM_B * doc_len / avgdl))
    return score


idf = {}
with open("../support/trec_idf.txt", "r", encoding='utf-8') as record_object:
    lines = list(record_object.readlines())
    for line in lines:
        tmp_data = line.replace('\n','').split(" ")
        idf[tmp_data[0]] = float(tmp_data[1])
average_idf = sum(map(lambda k: float(idf[k]), idf.keys())) / len(idf.keys())


relsfile = "../trec/04数据集/qrels.robust2004.txt"



with open(relsfile, "r", encoding='utf-8') as rel_object:
    lines = list(rel_object.readlines())
    ex = lines[0].replace('\n','').strip().split(' ')
    
    current_no = 0
    time = 0
    for line in lines:
        
        documents = []
        doc_nos = []
        #记录存储一个系列的问答
        ex = line.replace('\n','').strip().split(' ')
        
        if ex[0] != current_no :
            
            time+=1
            current_no = ex[0]
            print(current_no)
            d_file = open("../04_groups/" + str(current_no), "r", encoding='utf-8')
            
            #with open("../04_groups/" + str(current_no), "r", encoding='utf-8') as op_object:
            lines = list(d_file.readlines())
            for line in lines:
                doc_data = eval(line.replace('\n',''))
                #print(doc_data)
                documents.append(doc_data['content'][:5000])
                doc_nos.append(doc_data['doc_no'])
                
            #倒排索引构建
            
            inverted = {}
            processed_docs = word_split(documents)
            avgdl = sum(float(len(x)) for x in documents) / len(documents) 
            for index,processed_doc in enumerate(processed_docs):
                doc_len = len(processed_doc)
                
                doc_str = change(processed_doc)
                wordlist = keywords(doc_str,ratio=0.8, pos_filter = ['NN', 'JJ' , 'VB'], scores=True, split=True, lemmatize= True)
                
                #max_tv = wordlist[0][1]
                #min_tv = wordlist[-1][1]
                #base = max_tv - min_tv
                max_pos = len(wordlist)
                
                for idx,word_item in enumerate(wordlist):
                    word_pair = word_item[0].strip().split(' ')
                    for word in word_pair:
                        if word not in STOPWORDS:
                            docid_dict = inverted.setdefault(word, {})
                            
                            
                            counter = 0  
                            #docid_dict = {}
                            for item in processed_doc:
                                if word == item:
                                    counter += 1
                            
                            bm_score = get_score(word, counter, idf, doc_len, avgdl, average_idf)
                            
                            #bm_score = get_score(word, word_item[1], idf, doc_len, avgdl, average_idf)
                            
                            docid_dict[doc_nos[index]] = bm_score
                            #print(bm_score)
                            
                            #locations = inverted.setdefault(word, []) 
                            #locations.append(docid_dict)
                #print(inverted)
       
            
            #print(inverted)
            
            
            Inf = 0
            k = 8
            block_inverted = {}
            for word,list_item in inverted.items():
                #print(word,len(list_item))
                doc_id_list = []
                doc_score_list = []
                for doc_id, doc_score in list_item.items():
                    doc_id_list.append(doc_id)
                    doc_score_list.append(doc_score)
                    
                item_num = len(doc_score_list)
                block_num = math.ceil(item_num / k)
                #print(doc_id_list)
                #print(doc_score_list)
                #print(block_num)
                
                block_list = block_inverted.setdefault(word,[])
                for i_time in range(block_num):
                    block_dict = {}
                    block_dict["list"] = []
                    block_dict["max_score"] = max(doc_score_list)
                    temp_list = []
                    for i in range(k):
                        temp_index = doc_score_list.index(max(doc_score_list))
                        temp_list.append((doc_id_list[temp_index],doc_score_list[temp_index]))
                        doc_score_list[temp_index] = Inf
                        if k * i_time + i + 1 == item_num:
                            break
                    
                    block_dict["list"] = temp_list
                    block_list.append(block_dict)
            inverted = block_inverted
            
            '''
            
            inv_filename = "../04_group_tx_inv/textrank_txbm2/" + str(current_no)
            inv_tr_file = open(inv_filename,'w')
            for word,list_item in inverted.items():
                inv_tr_file.write(str(word)+':'+str(list_item)+'\n')
            inv_tr_file.close()
            
            d_file.close()
            
            print("finish " + str(current_no))
            '''
   


         

    








































