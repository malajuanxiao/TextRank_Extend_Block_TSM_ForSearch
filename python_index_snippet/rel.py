#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 20:43:47 2019

@author: leyv
"""



from xml.dom.minidom import parse
import xml.dom.minidom
import re
import os

doc_dict = {}
bm_doc_list = []

#LA_data

rootdir = "trec/disk/TREC-Disk-5/LATIMES/"
file_list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
for filename in file_list:
    filename = os.path.join(rootdir, filename)
    
    #对每个文件进行操作
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    # 在集合中获取所有文章
    docs = collection.getElementsByTagName("DOC")
    for doc in docs:
        #提取主要信息
        doc_no = doc.getElementsByTagName('DOCNO')[0]
        headline = doc.getElementsByTagName('HEADLINE')
        title = ""
        for item in headline:
            h_list = item.getElementsByTagName('P')
            for h_item in h_list:
                title += (" " + h_item.childNodes[0].data.strip())
        text = doc.getElementsByTagName('TEXT')
        
        content = ""
        content = title.strip()
        for item in text:
            p_list = item.getElementsByTagName('P')
            for p_item in p_list:
                content += (" " + p_item.childNodes[0].data.replace('\n',' ').strip())
        
        doc_dict[doc_no.childNodes[0].data.strip()] = content 
        #bm_doc_list.append(content)

print("finish LA")


#FBI_DATA

num_r = re.compile(r'<DOCNO>([\d\D]*)</DOCNO>')
title_r = re.compile(r'<H3>( *)<TI>([\d\D]*)</TI>( *)</H3>')
text_r = re.compile(r'<TEXT>(\n?)([\d\D]*)</TEXT>')

rootdir = "trec/disk/TREC-Disk-5/FBIS/"
file_list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
for filename in file_list:
    filename = os.path.join(rootdir, filename)
    #print(filename)
    with open(filename, "r", encoding='utf-8') as file:
        whole_str = str(file.read())
        doc_list = whole_str.split("<DOC>")
        doc_list = doc_list[1:]
        for doc_item in doc_list:
            num_object = re.search(num_r, doc_item)# num_r.match(raw_item)
            
            title_object = re.search(title_r, doc_item)
            text_object = re.search(text_r, doc_item)
            
            content = title_object.group(2).replace('\n',' ').strip() + ' ' + text_object.group(2).replace('\n',' ').strip()
            doc_dict[num_object.group(1).strip()] = content
            #bm_doc_list.append(content)

print("finish FBI")


#FT_DATA
rootdir = "trec/disk/TREC-Disk-4/FT/"
for filepath in os.listdir(rootdir):
    filepath = os.path.join(rootdir, filepath)
    #print(filename)
    for filename in os.listdir(filepath):
        filename = os.path.join(filepath, filename)
        
        
        #对每个文件进行操作
        DOMTree = xml.dom.minidom.parse(filename)
        collection = DOMTree.documentElement
        # 在集合中获取所有文章
        docs = collection.getElementsByTagName("DOC")
        for doc in docs:
            #提取主要信息
            doc_no = doc.getElementsByTagName('DOCNO')[0]
            
            headline = doc.getElementsByTagName('HEADLINE')[0]
            title = headline.childNodes[0].data.replace('\n',' ').strip()
            
            text = doc.getElementsByTagName('TEXT')[0]
            content = text.childNodes[0].data.replace('\n',' ').strip()
            
            doc_dict[doc_no.childNodes[0].data.strip()] = title + " " + content
            #bm_doc_list.append(title + " " + content)

print("finish FT")

#FR_DATA

rootdir = "trec/disk/TREC-Disk-4/FR94/"
for filepath in os.listdir(rootdir):
    filepath = os.path.join(rootdir, filepath)
    for filename in os.listdir(filepath):
        filename = os.path.join(filepath, filename)
        #print(filename)
        
        
        #对每个文件进行操作
        DOMTree = xml.dom.minidom.parse(filename)
        collection = DOMTree.documentElement
        # 在集合中获取所有文章
        docs = collection.getElementsByTagName("DOC")
        for doc in docs:
            #提取主要信息
            doc_no = doc.getElementsByTagName('DOCNO')[0]
            text = doc.getElementsByTagName('TEXT')[0]
            
            content = ""
            for item in text.childNodes:
                if item.nodeName == 'SUMMARY':
                    for sitem in item.childNodes:
                        if hasattr(sitem, 'data') and sitem.nodeName != '#comment' and sitem.data.replace('\n','').strip():
                            content += (" " + sitem.data.replace('\n','').strip())
                            #print( sitem.nodeName +":"+ sitem.data.replace('\n',''))
                
                elif item.nodeName == 'SUPPLEM':
                    for pitem in item.childNodes:
                        if hasattr(pitem, 'data') and pitem.nodeName != '#comment' and pitem.data.replace('\n','').strip():
                            content += (" " + pitem.data.replace('\n','').strip())
                            #print( pitem.nodeName +":"+ pitem.data.replace('\n',''))
                
                elif hasattr(item, 'data') and item.nodeName != '#comment' and item.data.replace('\n','').strip():
                    content += (" " + item.data.replace('\n','').strip())
      
            doc_dict[doc_no.childNodes[0].data.strip()] = content 
            #bm_doc_list.append(content)

print("finish FR")

corpus_size = len(bm_doc_list)
print(corpus_size)
'''
from nltk import stem
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from tqdm import tqdm
import match.bm25_tool as bm25


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







import math
from six import iteritems
from six.moves import xrange
from functools import partial



df ={}
#idf = {}



pbar = tqdm(total = corpus_size)
for idx,doc in enumerate(bm_doc_list):
    if idx%1000 == 0:
        pbar.update(1000)
    deal_doc = tokenize(doc)
    WordNetStem = stem.WordNetLemmatizer()
    for i,word in enumerate(deal_doc):
        deal_doc[i] = WordNetStem.lemmatize(word,"n")
    for i,word in enumerate(deal_doc):
        deal_doc[i] = WordNetStem.lemmatize(word,"v")
    deal_doc = [token for token in deal_doc if token not in STOPWORDS]
    
    
    for word in set(deal_doc):
        if word not in df:
            df[word] = 0
        df[word] += 1
    
        
    #bm_doc_list[idx] = deal_doc


pbar.close()

'''



'''
pbar = tqdm(total = len(df))
with open("support/trec_idf.txt", "w", encoding='utf-8') as record_object:
    time = 0
    for word, freq in iteritems(df):
        time +=1
        if time % 100 == 0:
            pbar.update(100)
        #idf[word] = math.log(corpus_size - freq + 0.5) - math.log(freq + 0.5)
        #math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
        print(corpus_size,freq)
        record_object.writelines(word + " " + str( math.log(corpus_size - freq + 0.5) - math.log(freq + 0.5))    )
        record_object.writelines("\n")

pbar.close()
'''

#print(len(doc_info))




relsfile = "trec/04数据集/qrels.robust2004.txt"


with open(relsfile, "r", encoding='utf-8') as rel_object:
    lines = list(rel_object.readlines())
    ex = lines[0].replace('\n','').strip().split(' ')
    
    current_no = ex[0]
    record_list = []
    bad = 0
    for line in lines:
        #记录存储一个系列的问答
        ex = line.replace('\n','').strip().split(' ')
        if ex[0] != current_no :
            with open("04_groups/" + str(current_no), "w", encoding='utf-8') as record_object:
                for record_item in record_list:
                    record_object.writelines(str(record_item) + "\n")
            print("finish " + str(current_no))
            current_no = ex[0]
            record_list = []
            bad = 0
        
        if ex[3] == '0':
            bad  += 1
            

        if ex[3] == '0' and bad % 3 == 3 :#(bad % 3 == 1 or bad % 3 == 0):
            pass

        else:
            record_dict = {}
            record_dict['doc_no'] = ex[2]
            record_dict['r'] = ex[3]
            record_dict['content'] = doc_dict[ex[2]]
            record_list.append(record_dict)
    
        if line == lines[-1]:
            with open("04_groups/" + str(current_no), "w", encoding='utf-8') as record_object:
                for record_item in record_list:
                    record_object.writelines(str(record_item) + "\n")
            current_no = ex[0]
            record_list = []
            bad == 0






#doc_info.append(doc_dict)





