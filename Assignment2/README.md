The code is divided into 4 modules: NetworkSetup, DataLoading, K_means, and KNN.

---------------NetworkSetup------------------
This module contains functions to deisgn a pandapower network and run a time series simulation with different conditions. 
This module doesn't have any bells and whistles: it is meant to make it convenient to create a dataset to use with the KNN and K-means clustering algorithms. 
At the end of the file, input parameters as well as what to include in the network can be chosen, as well as an output filename and folder for saving the data. 

--------------DataLoading--------------------
This module contains a few convenience functions for loading the dataset created with the NetworkSetup module. These are just there to make it simple to load the data,
and the different operating states to load are selected by adding or removing a filename from a list defined in the module. 

--------------K_means------------------------
This contains a class MMScaler which can scale a data set to a user specified range using the fit_transform method. It saves the parameters used for the transform,
which can then be used to transform e.g. validation data using the transform method, or to invert the scaling using the invert_transform method. 

The main class in this module is the KMeans class, which can perform k-means clustering. It includes help methods to load and scale/normalise data. 
Scaling the data to lie in the range [0,1] is important, as the centroids in the algorithm are initialised to be between 0 and one in every dimension in the init_centroids method. 

The class implements the assign_clusters method, which assigns every point in a data set to a centroid. It contains the method calculate_loss, which calculates the sum
of the distances from each data point to its assigned centroid. The update_centroids method updates the centroids as the mean position of all points belonging to that cluster.

The class has a run_clustering method, which runs assignment, loss calculation and centroid updates until the difference between the current loss and the previous loss is
smaller than some tolerance tol.

The find_best_cluster method runs the clustering algorithm n_iter times and returns the clustering with the lowest loss. This is to try to find a global minimum.

The find_optimal_n_centroids method runs the find_best_cluster algorithm for different numbers of centroids, to try to find the right number of clusters to use.
It returns the optimal clusters for each number of centroids in the specified range search_range together with the loss for those clusterings,
and the optimal number of centroids can be chosen by plotting the loss and using e.g. the elbow method. 

------------KNN----------
This module contains the class KNNClassifier, which implements k nearest neighbour classification. 
A class instance can be instantiated empty or with a dataset, and contains methods for scaling and normalising the data. 

The classify method takes an unlabeled point, a labeled dataset, and the number of neighbours to use ('k'). It then calculates the distances from the unlabeled point to
all points in the labeled dataset, and assigns a class given by the most common class among the k nearest neighbours. 

The find_best_k method takes a dataset of labeled points and tries to find the best k to use by calculating the accuracy of the classification algorithm for different k:s,
using a proportion of the dataset for classification given by prop_test. 

The classify_many method takes an unlabeled dataset, a labeled dataset and a parameter k, and classifies the unlabeled data using the k nearest neighbours in the labeled dataset. 

