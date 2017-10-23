# Midterm

**Team members**
1. Chao-Ching Chiang
2. Bailin Wang
3. Jin Zhang

**Datasets**

[USA Geolocated Twitter dataset](http://followthehashtag.com/datasets/free-twitter-dataset-usa-200000-free-usa-tweets/)



## Analyze hashtags in tweets

package networkx is required.
Out first goal it to analyze hashtags in tweets and rank them using different metrics.
### Preprocessing 

* extract the hashtags based on regular expression.
* we only extract hashtags that is important enough, thus we set a threshold for the count of hashtags so that we can observe the most influential ones.
* Based on the extracted hashtags, we construct a weighted, undirected graph based on their co-occurence in the tweets.

### Visualizaing Text

After we construct the co-occurenece graph, we use serveral metrics to evaluate the importance of these hashtags:

* Weighted PageRank
* Degree centrality
* Closeness centrality
* Betweenness centrality

### Clustering

We use K-means and SpectralClustering algorithm to cluster the hashtags. We build an interactive scatter plot to visualize the results.
Interactive version of it can be see running:
   
    bokeh serve --show hashtag.py

### Explaination


## Analyze text in tweets
package wordcloud is required.

### Preprocessing 

* all numbers are replaced with a speical symbol \$NUM\$
* special character like #, ! are removed
* URL links are removed
* tokenization by space

### Visualizaing Text

in wordcloud.ipynb

### Clustering

Each tweet is represented using a word-count vectors.Basically, two cluster algorithms KMeans and Birch are employed. To visualize the high-dimensional vectors, t-sne is used to reduce the dimentionality to 2d so that they can be easily plotted.
run the following command

	bokeh serve --show cluster.py

**visualization**
Slide bars of adjusting the number of clusters are embedded for interactive visualization.

### Explaination

