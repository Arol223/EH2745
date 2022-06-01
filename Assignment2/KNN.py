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


def data_split(data, prop_test=0.3):
    data_len = data.shape[0]
    test_set_len = round(data_len * prop_test)
    test_inds = randint(0, data_len - 1, size=test_set_len)
    train_inds = [i for i in range(data_len) if i not in test_inds]
    train_set = data.iloc[train_inds]
    test_set = data.iloc[test_inds]
    return train_set, test_set
    
    
class KNNClassifier:
    
    def __init__(self, *args, **kwargs):
        if "data" in kwargs.keys():
            data = kwargs["data"]
            self.data.iloc[:,:-1] = self.scale_data(data.iloc[:,:-1]) #Don't scale labels, they are in last col by convention
    
    def classify(self, k, point, data=None):
        if data is None:
            data = self.data
    
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
    
    def find_neighbours(self, k, point, data=None):
        if data is None:
            data = self.data
        else: 
            data.iloc[:,:-1] = self.scale_data(data.iloc[:,:-1], mode="init")
        point.iloc[:-1] = self.scale_data(point.iloc[:-1], mode="use_old")
        dists = pd.DataFrame(norm(data.iloc[:,:-1].to_numpy()) - point.iloc[:-1].to_numpy(), columns="Distance")
        dists["Cluster"] = data["Cluster"]
        KNN = dists.nsmallest(k, columns="Distance")
        cluster = KNN["Cluster"].mode() # Find the most common class
        return cluster
    
    
    
    
        
        
        
        
        # Takes k neighbours to use, input data to classify and 