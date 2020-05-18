#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:23:19 2019

@author: leyv
"""


#trec/disk/TREC-Disk-5/LATIMES/LA010198


 
from xml.dom.minidom import parse
import xml.dom.minidom
import re
import os
import match.bm25_tool as bm25

doc_info = []
doc_list = []





with open("LA_RAW", "w", encoding='utf-8') as record_object:
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
            doc_dict = {}
            #提取主要信息
            doc_no = doc.getElementsByTagName('DOCNO')[0]
            headline = doc.getElementsByTagName('HEADLINE')
            title = ""
            for item in headline:
                h_list = item.getElementsByTagName('P')
                for h_item in h_list:
                    title += (" " + h_item.childNodes[0].data.strip())
            text = doc.getElementsByTagName('TEXT')
            
            ph_list = []
            ph_list.append(title.strip())
            for item in text:
                p_list = item.getElementsByTagName('P')
                for p_item in p_list:
                    ph_list.append(p_item.childNodes[0].data.strip())
                    #print(p_item.childNodes[0].data.strip())
            
            
            doc_dict['doc_no'] = doc_no.childNodes[0].data 
            doc_dict['content'] = ph_list
            
            #record_object.writelines(str(doc_dict))
            doc_info.append(doc_dict)
    
    pass
    
with open("FBI_RAW", "w", encoding='utf-8') as record_object:
    #FBI_DATA
    
    num_r = re.compile(r'<DOCNO>([\d\D]*)</DOCNO>')
    title_r = re.compile(r'<H3>( *)<TI>([\d\D]*)</TI>( *)</H3>')
    text_r = re.compile(r'<TEXT>(\n?)([\d\D]*)</TEXT>')
    
    rootdir = "trec/disk/TREC-Disk-5/FBIS/"
    file_list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for filename in file_list:
        filename = os.path.join(rootdir, filename)
        with open(filename, "r", encoding='utf-8') as file:
            whole_str = str(file.read())
            doc_list = whole_str.split("<DOC>")
            doc_list = doc_list[1:]
            for doc_item in doc_list:
                doc_dict = {}
                num_object = re.search(num_r, doc_item)# num_r.match(raw_item)
                doc_dict['doc_no'] = num_object.group(1).strip()
                
                title_object = re.search(title_r, doc_item)
                text_object = re.search(text_r, doc_item)
                doc_dict['content'] = title_object.group(2).replace('\n',' ').strip() + ' ' + text_object.group(2).strip()
                
                doc_info.append(doc_dict)
                #print(title_object.group(2).replace('\n',' ').strip())
                #print(text_object.group(2).replace('\n',' ').strip())
            #print(len(doc_list))
    
    pass


        
    
    
    
with open("FT_RAW", "w", encoding='utf-8') as record_object:
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
                doc_dict = {}
                #提取主要信息
                doc_no = doc.getElementsByTagName('DOCNO')[0]
                
                
                headline = doc.getElementsByTagName('HEADLINE')[0]
                title = headline.childNodes[0].data.strip()
                
          
                text = doc.getElementsByTagName('TEXT')[0]
                content = text.childNodes[0].data.strip()
        
                
                #print(filename, doc_no.childNodes[0].data.strip())
                doc_dict['doc_no'] = doc_no.childNodes[0].data 
                doc_dict['content'] = title + " " + content
                #print(doc_dict)
                #record_object.writelines(str(doc_dict))
                doc_info.append(doc_dict)
            #print(filename)
    
    pass
    
    
with open("FR_RAW", "w", encoding='utf-8') as record_object:
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
                doc_dict = {}
                #提取主要信息
                doc_no = doc.getElementsByTagName('DOCNO')[0]
                
                
                text = doc.getElementsByTagName('TEXT')[0]
                
                content = ""
                #print(filename + doc_no.childNodes[0].data)
                #print(text.childNodes)
                
                for item in text.childNodes:
                    if item.nodeName == 'SUMMARY':
                        for sitem in item.childNodes:
                            if hasattr(sitem, 'data') and sitem.nodeName != '#comment' and sitem.data.replace('\n',''):
                                content += (" " + sitem.data.replace('\n',''))
                                #print( sitem.nodeName +":"+ sitem.data.replace('\n',''))
                    
                    elif item.nodeName == 'SUPPLEM':
                        for pitem in item.childNodes:
                            if hasattr(pitem, 'data') and pitem.nodeName != '#comment' and pitem.data.replace('\n',''):
                                content += (" " + pitem.data.replace('\n',''))
                                #print( pitem.nodeName +":"+ pitem.data.replace('\n',''))
                    
                    elif hasattr(item, 'data') and item.nodeName != '#comment' and item.data.replace('\n',''):
                        content += (" " + pitem.data.replace('\n',''))
                        #print( item.nodeName +":"+ item.data.replace('\n',''))
                    
                    #print(item.nodeName)
                    
                '''
                summary = text.getElementsByTagName('SUMMARY')
                
                if summary.length > 0:
                    print(summary)
                    for item in summary.item(0).childNodes:
                    
                        if hasattr(item, 'data') and item.nodeName != '#comment' and item.data.replace('\n',''):
                           print( item.nodeName +":"+ item.data)
                       #print(summary.item(0).childNodes[2].data.strip())#.childNodes[0].data.strip())
                
                
                
                supplem = text.getElementsByTagName('SUPPLEM')
                
                if supplem.length > 0:
                    print(supplem)
                    for item in supplem.item(0).childNodes:
                    
                        if hasattr(item, 'data') and item.nodeName != '#comment' and item.data.replace('\n',''):
                           print( item.nodeName +":"+ item.data)
                       #print(supplem)#.childNodes[0].data.strip())
                '''
          
        
                doc_dict['doc_no'] = doc_no.childNodes[0].data 
                doc_dict['content'] = content
                #print(doc_dict)
                #record_object.writelines(str(doc_dict))
                doc_info.append(doc_dict)
                #print(filename)
    
    
    pass    
print(len(doc_info))


"""

doc_info = []
filename = "trec/disk/TREC-Disk-5/LATIMES/LA010189"
# 使用minidom解析器打开 XML 文档
DOMTree = xml.dom.minidom.parse(filename)
collection = DOMTree.documentElement
if collection.hasAttribute("shelf"):
    print("Root element : %s" % collection.getAttribute("shelf"))
 
# 在集合中获取所有文章
docs = collection.getElementsByTagName("DOC")

# 打印每部电影的详细信息
for doc in docs:
    '''
    if movie.hasAttribute("title"):
        print "Title: %s" % movie.getAttribute("title")
    '''
    doc_dict = {}
    doc_no = doc.getElementsByTagName('DOCNO')[0]
    headline = doc.getElementsByTagName('HEADLINE')
    title = ""
    for item in headline:
        h_list = item.getElementsByTagName('P')
        for h_item in h_list:
            title += (" " + h_item.childNodes[0].data.strip())
    text = doc.getElementsByTagName('TEXT')
    
    
    ph_list = []
    ph_list.append(title.strip())
    for item in text:
        p_list = item.getElementsByTagName('P')
        for p_item in p_list:
            ph_list.append(p_item.childNodes[0].data.strip())
            #print(p_item.childNodes[0].data.strip())
    
    
    doc_dict['doc_no'] = doc_no.childNodes[0].data
    #doc_dict['title'] = 
    doc_dict['content'] = ph_list
    
    doc_info.append(doc_dict)
    



"""







"""
rootdir = "trec/disk/TREC-Disk-4/FR94/"   
for filepath in os.listdir(rootdir):
    filepath = os.path.join(rootdir, filepath)
    print(filepath)
    for filename in os.listdir(filepath):
        
        filename = os.path.join(filepath, filename)
        print(filename)
        rewrite_flag = 0
        new_str = ''
        
        
        with open(filename, "r", encoding='utf-8') as file:
            doc_str = str(file.read())
            if '<all>' not in doc_str:
                rewrite_flag = 1
                new_str = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
            <all>\n''' + doc_str + '\n</all>'
                
        print(filename +" "+ str(rewrite_flag))
        
        if rewrite_flag == 1:
            with open(filename, "w", encoding='utf-8') as file:
                file.write(new_str)
"""

