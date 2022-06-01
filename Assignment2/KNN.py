# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:05:58 2022

@author: arvidro
"""
import numpy as np
from numpy.linalg import norm
from numpy.random import random as rand
import pandas as pd
from DataLoading import get_all
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from numpy.random import randint
import random
from K_Means import KMeans

def data_split(data, prop_test=0.3):
    data_len = data.shape[0]
    test_set_len = round(data_len * prop_test)
    train_inds = np.arange(data_len)
    test_inds = random.sample(range(data_len), test_set_len)
    train_inds = np.delete(train_inds, test_inds)

    train_set = data.iloc[train_inds]
    test_set = data.iloc[test_inds]
    return train_set, test_set
    
    
class KNNClassifier:
    
    def __init__(self, *args, **kwargs):
        if "data" in kwargs.keys():
            self.data = kwargs["data"]
            self.data.iloc[:,:-1] = self.scale_data(data.iloc[:,:-1]) #Don't scale labels, they are in last col by convention
    
    def scale_data(self, data, mode="init"):
        data_np = data.to_numpy()
        if mode == "init":
            scaler = MinMaxScaler()
            data_np = scaler.fit_transform(data_np)
            self.scaler = scaler
        elif mode == "use_old": # uses scaler with existing transform 
            scaler = self.scaler  
            data_np = scaler.transform(data_np)
        
        cols = data.columns 
        ind = data.index 
        scaled_df = pd.DataFrame(data_np, index=ind, columns=cols)
        return scaled_df
    def inverse_scaling(self, scaled_data):
        scaler = self.scaler
        data_np = scaled_data.to_numpy()
        data_np = scaler.inverse_transform(data_np)
        cols = scaled_data.columns 
        ind = scaled_data.index 
        unscaled_df = pd.DataFrame(data_np, index=ind, columns=cols)
        return unscaled_df 
    
    def classify(self, k, point, data=None, class_col=None):
        if data is None:
            data = self.data
        if class_col is None:
            class_col = "Cluster" # which column has the classes
        point_len = len(point) - 1
        #point.iloc[:-1] = self.scale_data(point.iloc[:-1], mode="use_old")
        dists = pd.DataFrame()
        dists["Distance"] = norm(
            data.iloc[:,:-1].to_numpy()
            - point.iloc[:-1].to_numpy().reshape([1,point_len]), axis=1
            )
        dists[class_col] = data[class_col]
        KNN = dists.nsmallest(k, columns="Distance")
        cluster = KNN[class_col].mode() # Find the most common class
        return cluster.to_numpy()[0]
    
    def find_best_k(self, data, k_max, class_col=None, prop_test=0.3):
        if class_col is None:
            class_col = "Cluster"
        train, test = data_split(data, prop_test)
        train.reset_index(inplace=True, drop=True)
        test.reset_index(inplace=True, drop=True)
        
        
        accs = []
        for k in range(1, k_max):
            res = []
            for i in range(test.shape[0]):
                point = test.iloc[i]
                truth = point[class_col]
                c = self.classify(k, point, data=train, class_col=class_col)
                res.append(c == truth)
            
            acc = sum(res)/len(res)
            accs.append(acc)
        return accs
if __name__ == '__main__':
    
    #data = pd.read_csv("Data/Scaled_labeled_data.csv", index_col=0)
    data = get_all() 
    KNN = KNNClassifier()
    accs = KNN.find_best_k(data, 20, class_col="Class", prop_test=0.3)
    
    plt.plot(np.array(accs) * 100)
    plt.xlabel("k")
    plt.ylabel("Accuracy %")
    #KNN = KNNClassifier(data=train)
    #c = KNN.find_neighbours(5, test.iloc[1])