# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:02:50 2022

@author: arvidro
"""

import numpy as np
from numpy.linalg import norm
from numpy.random import random as rand
import pandas as pd
from DataLoading import get_all
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

class KMeans:
    
    def __init__(self, *args, **kwargs):   
        self.load_data()
        self.data = self.scale_data()
    
    def load_data(self):
        self.data = get_all(include_class=False)
        
    def normalise_data(self):
        data = self.data
        cols = data.shape[1]
        
        means, stds = np.zeros(cols), np.zeros(cols)
         
        for i in range(cols):
            col = data.iloc[:, i].to_numpy()
            mean = col.mean()
            std = col.std()
            col = (col - mean) / std
            data.iloc[:,i] = col
            means[i] = mean
            stds[i] = std 
        self.data = data
        self.means = means 
        self.stds = stds 
    def scale_data(self, in_data=None):
        if in_data is None:
            in_data = self.data
        scaler = MinMaxScaler()
        data = in_data.to_numpy()
        data = scaler.fit_transform(data)
        in_data.iloc[:,:] = data
        self.scaler = scaler         
        return in_data
    
    def get_inverse_norm_data(self):
        
        data = self.data
        cols = data.shape[1]
        
        for i in range(cols):
            col = data.iloc[:, i].to_numpy()
            mean = self.means[i]
            std = self.stds[i]
            
            col = col * std + mean 
            data.iloc[:, i] = col
        
        return data
    
    def get_unscaled_data(self):
        return self.scaler.inverse_transform(self.data.to_numpy())
    
    def init_centroids(self, n_clusters):
        dims = self.data.shape[1]
        centroids = rand([dims, n_clusters])

        return centroids
    
    def assign_clusters(self, centroids=None, data=None, scale=True):
        if centroids is None:
            centroids = self.centroids
        n_clusters = centroids.shape[1]
        dims = centroids.shape[0]
        if data is None:
            data = self.data
        if scale:
            data = self.scale_data(data)
        data = data.to_numpy()
        diffs = np.array([ # get the differences to be able to assign centroids
            data - centroids[:, i].reshape([1, dims]) for i in range(n_clusters)
            ])
        
        norms = np.linalg.norm(diffs, axis=2) # Calculate 2 norms for all the vectors
        clusters = np.argmin(norms, axis=0) # Cluster is the index of the smallest norm

        return pd.Series(clusters, name="Cluster")
    
    def calculate_loss(self, centroids=None, data=None, clusters=None):
        if centroids is None:
            centroids = self.centroids
        if data is None:
            data = self.data
        if clusters is None:
            clusters = self.clusters
        n_clusters = centroids.shape[1]
        dims = centroids.shape[0]
        data = pd.concat([data, clusters],axis=1).set_index("Cluster")
        loss = 0
        for i in range(n_clusters):
            try:
                points = data.loc[[i]]
                diffs = np.sqrt((points - centroids[:,i].reshape([1, dims])) ** 2)
                loss += np.sum(np.sum(diffs))
            except KeyError:
                continue      
                

        return loss
    def update_centroids(self, centroids=None, data=None, clusters=None):
        if centroids is None:
            centroids = self.centroids
        if data is None:
            data = self.data
        if clusters is None:
            clusters = self.clusters
        n_clusters = centroids.shape[1]
        data = pd.concat([data, clusters], axis=1).set_index("Cluster")
        new_centroids = np.zeros(centroids.shape)
        for i in range(n_clusters):
            try:
                points = data.loc[i]
                new = points.mean(axis=0) # Update the centroid as the mean of the points in all dims
                new_centroids[:, i] = new
            except KeyError:
                #print("No points in cluster {}".format(i))
                continue
        diff = np.sqrt((new_centroids - centroids) ** 2)
        diff = norm(diff, axis=0)
        diff = np.sum(diff)
        return new_centroids, diff
    
    def run_clustering(self, tol=1e-5, data=None, centroids=None):
        if centroids is None:
            centroids = self.centroids
        if data is None:
            data = self.data
        
        diff = 1000
        while diff > tol: 
            clusters = self.assign_clusters(centroids, data)
            centroids, diff = self.update_centroids(centroids, data, clusters)
        loss = self.calculate_loss(centroids, data, clusters)
        return centroids, loss
    
    def find_best_cluster(self, n_centroids, tol=1e-5, n_iter=100, data=None):
        clustering_list = []
        losses = []
        for i in range(n_iter):
            centroids = self.init_centroids(n_centroids)
            centroids, loss = self.run_clustering(
                tol=tol, data=data, centroids=centroids
                )
            clustering_list.append(centroids)
            losses.append(loss)
        ind = np.argmin(losses)
        opt_centroids = clustering_list[ind]
        return opt_centroids, clustering_list, losses
    
    def find_optimal_n_centroids(self, search_range, tol=1e-5, n_iter=100, data=None):
        losses = []
        centroids = []
        start = search_range[0]
        stop = search_range[1]
        for i in range(start, stop):
            opt, clust, loss = self.find_best_cluster(i, tol, n_iter, data)
            losses.append(min(loss))
            centroids.append(opt)
        return centroids, losses
    
    def find_elbow(self, losses):
        diffs = [losses[i - 1] - losses[i] for i in range(1,len(losses))]
        for i in range(1, len(diffs)):
            prev = diffs[i - 1]
            curr = diffs[i]
            if curr < prev/10:
                return i - 1
if __name__ == '__main__':
    km = KMeans()
    centroids, losses = km.find_optimal_n_centroids([1, 12])
    plt.plot(np.arange(1,12), losses)
    plt.xlabel("Number of clusters")
    plt.ylabel("Loss")