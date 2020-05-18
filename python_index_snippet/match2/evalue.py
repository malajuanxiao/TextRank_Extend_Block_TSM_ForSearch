# -*- coding: utf-8 -*-
import numpy as np


class Evalue(object):
    def __init__(self,doc_sum):
        
        self.lstep = 0
        if doc_sum <= 50:
            self.lstep = 5
        else:
            self.lstep = 10
            
            
        self.plv = []
        self.rlv = []
        
    
    def emrr(self,score_list,que_index,que_docs,rel_docs):
        self.plv = []
        self.rlv = []
        print ("*************开始输出MRR相关结果*************")
        
        #for k in range(self.lstep,len(que_docs)+1,self.lstep):
        for k in range(1,len(que_docs)+1,1):
            
            MRRS = 0
            MRR = 0
            
            for idx,qu_index in enumerate(que_index[:k]):
                Recovery = []
                Precision = []
                qu_index = idx
                #print(len(score_list),len(que_docs)+1,len(score_list[idx]),k)
                find_flag = 0
            
                K = 30
                for i in range(K):
                    if score_list[idx][i][0] in rel_docs[idx]:
                        find_flag = 1
                        MRRS +=  1/(i + 1.0)
                        break
                    
                        
                if find_flag == 0:
                    MRRS +=  1/30
                    
            MRR = MRRS/k
            print("MRR指标:",MRR)
            print ("***********前"+str(k)+"************")
                        
           
            
            
            
            
            
            
            
        
        
    
    
    def eva(self,score_list,que_index,que_docs,rel_docs):
        self.plv = []
        self.rlv = []
        print ("*************开始输出PR相关结果*************")
        
        #for k in range(self.lstep,len(que_docs)+1,self.lstep):
        for k in range(1,len(que_docs)+1,1):
            Recovery_list = []
            Precision_list = []
        
            for idx,qu_index in enumerate(que_index[:k]):
                Recovery = []
                Precision = []
                qu_index = idx
                #print(len(score_list),len(que_docs)+1,len(score_list[idx]),k)
            
                have = 0
                K = 5
                for i in range(K):
                    if score_list[idx][i][0] in rel_docs[idx]:
                        have +=1
                Recovery.append(have*1.0/float(len(rel_docs[qu_index])))
                Precision.append(have*1.0/(K*1.0))
            
                have = 0
                K = 10
                for i in range(K):
                    if score_list[idx][i][0] in rel_docs[idx]:
                        have +=1
                Recovery.append(have*1.0/float(len(rel_docs[qu_index])))
                Precision.append(have*1.0/(K*1.0))
            
                have = 0
                K = 20
                for i in range(K):
                    if score_list[idx][i][0] in rel_docs[idx]:
                        have +=1
                Recovery.append(have*1.0/float(len(rel_docs[qu_index])))
                Precision.append(have*1.0/(K*1.0))
                
                have = 0
                K = 30
                for i in range(K):
                    if score_list[idx][i][0] in rel_docs[idx]:
                        have +=1
                Recovery.append(have*1.0/float(len(rel_docs[qu_index])))
                Precision.append(have*1.0/(K*1.0))
            
                Recovery_list.append(Recovery)
                Precision_list.append(Precision)
            
            #print("Recovery:\n",Recovery_list)
            #print("Precision:\n",Precision_list)
            Recovery_avg = (np.array(Recovery_list).sum(axis=0))/len(Recovery_list)
            Recovery_avg = np.around(Recovery_avg,3)
            
            Precision_avg = (np.array(Precision_list).sum(axis=0))/len(Precision_list)
            Precision_avg = np.around(Precision_avg,3)
            self.rlv.append(Recovery_avg)
            self.plv.append(Precision_avg)
            print("Recovery:",Recovery_avg,"\nPrecision:",Precision_avg)
        
        
            print ("***********前"+str(k)+"************")
            print ("***************************")
        return Precision_list,Recovery_list
        #print(self.plv)
        #print(self.rlv)
        
            
            



