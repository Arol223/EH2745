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


class KNNClassifier:
    
    def __init__(self, data):
        self.data = data
    
    def classify(self, k, point, data=None):
        if data is None:
            data = self.data
    
    def scale_data(self, data):
        scaler = MinMaxScaler()
        data_np = data.to_numpy()
        data_np = scaler.fit_transform(data)
        self.scaler = scaler
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
        data = data.iloc[:, :len(point)].to_numpy()
        
        # Takes k neighbours to use, input data to classify and 