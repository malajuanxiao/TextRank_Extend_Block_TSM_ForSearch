#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 16:56:38 2019

@author: leyv
"""


import re

filename = 'trec/04数据集/04.testset'
file = open(filename)
qu_set = str(file.read())
#print(qu_set)
file.close()
raw_list = qu_set.split('</top>')



#print(raw_list[9])
'''
num_r = re.compile(r'<title>(\n?)(.*)\n')
test_str = "<title>\nU.S. ethnic population\n\n<desc> Description: "
test_str = "<title>\nU.S. ethnic population\n\n<desc> Description: "
print(test_str)
num_object = re.search(num_r, test_str)# num_r.match(raw_item)

print(num_object.group(2) )

'''

num_r = re.compile(r'Number:(.*)\n')
title_r = re.compile(r'<title>(\n?)([\d\D]*)\n<desc>')
desc_r = re.compile(r'<desc>(\n?)([\d\D]*)\n<narr>')
narr_r = re.compile(r'<narr>(\n?)([\d\D]*)')


qu_list = []
for raw_item in raw_list[:-1]:
    qu_dict = {}
    print(raw_item)
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
print(len(raw_list))
print(raw_list[0])
print(qu_list[0])
