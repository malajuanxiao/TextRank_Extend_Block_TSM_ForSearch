# -*- coding: utf-8 -*-


from nltk import stem
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
import re
from tqdm import tqdm
import bm25_tool as bm25
import time

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

#print(len(raw_list))

#print(test_dict['index'])
test_dict = qu_list[0]
top_5_plist = []
top_5_rlist = []
top_10_plist = []
top_10_rlist = []
top_20_plist = []
top_20_rlist = []



load_status = 0
idf = {}
qu_list = qu_list[:40]
pbar = tqdm(total = len(qu_list))
for test_dict in qu_list:
    pbar.update(1)
    qu_doc = Stem_qu(tokenize(test_dict['content']))
    docno_list = []
    rel_list = []
    origin_docs = []
    all_rela = 0
    with open("../04_groups/" + test_dict['index'], "r", encoding='utf-8') as target_object:
        lines = list(target_object.readlines())
        for line in lines:
            doc_data = eval(line.replace('\n',''))
            origin_docs.append(doc_data['content'])
            rel_list.append(doc_data['r'])
            docno_list.append(doc_data['doc_no'])
            if doc_data['r'] != "0":
                #print(doc_data['r'])
                all_rela += 1
                
            
    
    
    
    
    
    
    
    processed_raw_docs = [tokenize(doc) for doc in origin_docs]
    processed_docs = Stem_voca(processed_raw_docs)
    
    if load_status == 0:
        bm25Model = bm25.BM25(processed_docs,{},2)
        load_status = 1
        idf =  bm25Model.idf
    else:
        bm25Model = bm25.BM25(processed_docs,idf,3)
        
        
    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
    
    score_dict = {}
    scores = bm25Model.get_scores(qu_doc,average_idf)
    for idx,score_item in enumerate(scores):
        score_dict[idx] = score_item
    
    
    
    score_list = sorted(score_dict.items(), key = lambda score_dict:score_dict[1],reverse=True)
    rela = 0
    find_all = 10000
    for i,score_item in enumerate(score_list[:10]):
        rel_str = rel_list[ int(score_item[0])]
        if rel_str != '0':
            rela+=1
            if rela == all_rela:
                find_all = i
        
    top_5_plist.append((rela*1.0) / min(find_all,10))
    top_5_rlist.append((rela*1.0) / all_rela)
        
    
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





    
"""
qu_sum = len(top_5_plist)
print(qu_sum) 

avg_5_p = 0
avg_5_r = 0
avg_10_p = 0
avg_10_r = 0
avg_20_p = 0
avg_20_r = 0

print(sum(top_5_plist)/qu_sum, 
      sum(top_10_plist)/qu_sum, 
      sum(top_20_plist)/qu_sum,
      sum(top_5_rlist)/qu_sum,
      sum(top_10_rlist)/qu_sum,
      sum(top_20_rlist)/qu_sum)



rela = 0
for score_item in score_list[:5]:
    rel_str = rel_list[ int(score_item[0])]
    print(rel_str)
    if rel_str != '0':
        rela+=1
    
print(rela*1.0/30)
"""




"""
import fileDeal as fd
import process as pp

'''
0.重要参数
'''
#使用何种数据
#c_data = "npl_data"
#c_data = "med_data"
c_data = "LISA_data"

#使用何种方法
Match_fun = "wordSim1"
#Match_fun = "wordSim2"
#Match_fun = "bm25"
#Match_fun = "wmd"
#Match_fun = "lmj"


w2v_kind = 1
word2vec = []
if Match_fun == "wmd" or Match_fun == "wordSim1" or Match_fun == "wordSim2":
    import gensim
    if w2v_kind == 1:
        word2vec = gensim.models.KeyedVectors.load_word2vec_format('~/python_workspace/datahouse/glove-wiki-gigaword-100/glove-wiki-gigaword-100.txt',binary=False)
    elif w2v_kind == 2:
        word2vec = gensim.models.KeyedVectors.load_word2vec_format('~/python_workspace/datahouse/glove.6B/glove.6B.100d.txt',binary=False)
    elif w2v_kind == 3:
        word2vec = gensim.models.KeyedVectors.load_word2vec_format('~/python_workspace/datahouse/word2vec-google-news-300/GoogleNews-vectors-negative300.bin',binary=True)


'''
1.数据提取
'''
tdata = fd.FileDeal(c_data)


#记录候选文档和文档编号为
documents = tdata.documents
file_index = tdata.file_index  
#print(file_index[3809])
#记录查询文本和查询编号为
que_documents = tdata.que_documents
que_index = tdata.que_index
#结果集对应查询和答案文本编号为
rel_index = tdata.rel_index
rel_docs = tdata.rel_docs

print("In the doc-text dataset there are", len(documents), "textual documents")
print("In the query-text dataset there are ",len(que_index),"query documents")
print("In the rlv-ass dataset there are ",len(rel_docs),"answers")


'''
print(file_index[:3],len(file_index))
print(documents[:3])
print(que_index[:3],len(que_index))
print(que_documents[:3])

print(rel_index,len(rel_index))
print(rel_docs)
'''

'''
2.数据预处理
'''
#all_que_slices  all_doc_slices 为按句子切分的查询候选片段   que_docs processed_docs 为一般化处理的查询候选文档
preprocess = pp.PreProc(que_documents,documents)
all_que_slices = preprocess.Puncut(0)
all_doc_slices = preprocess.Puncut(1)
que_docs,processed_docs = preprocess.Normal()

#print(all_doc_slices[:3])
#print(len(all_que_slices))
#print(all_que_slices[6])

#all_que_slices = all_que_slices[:3]
#que_docs = que_docs[:3]

docs_have = preprocess.FetchDocs(c_data, que_docs)




'''
3.数据碎片化机制
'''

import matchTool

ma = matchTool.Match(processed_docs,word2vec,1)
#print(ma.idfmax)
sni1_score_list = ma.getwordsim1(all_doc_slices,all_que_slices,rel_docs,docs_have,file_index,3)
#sni1_score_list = ma.getsimwmd(all_doc_slices,all_que_slices,rel_docs,docs_have,file_index,3)


#ma = matchTool.Match(processed_docs,[],0)
#ma.getsimlmj(all_doc_slices,all_que_slices,rel_docs,docs_have,file_index,1)
#sni1_score_list = ma.getsimbm25(all_doc_slices,all_que_slices,rel_docs,docs_have,file_index,3)
#sni1_score_list = ma.getsimlmj(all_doc_slices,all_que_slices,rel_docs,docs_have,file_index,1)



'''
3.原始方案
'''

import maOrigin
mo = maOrigin.MatchOrigin(processed_docs,que_docs,file_index,docs_have,word2vec)     #原始方案初始化
mo.getMatch(Match_fun)                                            #开始匹配
score_list = mo.score_list



'''
import maMusnippet

ma = maMusnippet.MatchMusnippet(processed_docs,que_docs,file_index,docs_have,word2vec)

ma.getMatch(Match_fun,filter_score = 1.0,limit_length = 5,limit_ratio = 0.5, ing_fun = 2)
sni1_score_list = ma.sni_score_list
ma.getMatch(Match_fun,filter_score = 1.0,limit_length = 5,limit_ratio = 0.5, ing_fun = 3)
sni2_score_list = ma.sni_score_list

'''


'''
评估结果
'''
import evalue
eva = evalue.Evalue(len(que_docs))

#原始方法评估
#eva.emrr(score_list,que_index,que_docs,rel_docs)
#eva.emrr(sni1_score_list,que_index,que_docs,rel_docs)
        
pl,rl = eva.eva(score_list,que_index,que_docs,rel_docs)
plv = eva.plv
rlv = eva.rlv
sni1_pl,sni1_rl = eva.eva(sni1_score_list,que_index,que_docs,rel_docs)
sni1_plv = eva.plv
sni1_rlv = eva.rlv

import resultShow 
rs = resultShow.ResultShow
dis_list = rs.show_dispa(pl,rl,sni1_pl,sni1_rl,0)
print(dis_list)




'''

print(rel_docs[5])
print(sni1_score_list[5][:20])
print(score_list[5][:20])

print(que_index[4],":",que_documents[4],"\n",all_que_slices[4])
print(que_index[5],":",que_documents[5],"\n",all_que_slices[5])

z_d = [1309,2420,3404,5795]
f_d = [663,3599,3809,5920]

for i in z_d:
    print(file_index[i],":",documents[i],"\n",all_doc_slices[i])
    
print("***********************")
for i in f_d:
    print(file_index[i],":",documents[i],"\n",all_doc_slices[i])
'''


"""
