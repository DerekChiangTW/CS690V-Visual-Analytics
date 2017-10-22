#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import networkx as nx
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row, widgetbox
from bokeh.models.glyphs import Text
from bokeh.models import ColumnDataSource, Slider, HoverTool, LabelSet
from utils import extract_hashtags, count_cooccurence
from bokeh.models.widgets import Select, Div
from sklearn.cluster import KMeans, SpectralClustering


THRESHOLD = 700
METHODS = ['K-means', 'Spectral']
COLORS = ['#ae254a', '#007380', '#4364ae', '#f9d500',
          '#ff7256', '#800080', '#0e2f44', '#f442cb']
PLOT1_PARAM = {'plot_height': 400, 'plot_width': 400, 'toolbar_location': None}
PLOT2_PARAM = {'plot_height': 400, 'plot_width': 600, 'toolbar_location': None}
DEFAULT_TICKERS = ['PageRank',
                   'Degree centrality',
                   'Closeness centrality',
                   'Betweenness centrality']


def nix(val, lst):
    return [x for x in lst if x != val]


def get_data(t1, t2, alg, clusters):
    """ Get the data according to user's settings.

    Parameters
    ----------
        t1 : string
            The selected score for x axis.

        t2 : string
            The selected score for y axis.

        alg : string
            The selected clustering algorithm.

        clusters : int
            The number of clusters.

    Returns
    -------
        data : dict
            A dictionary which contains the DataSource for the plot.

    """
    # Run K-means clustering
    if alg == METHODS[0]:
        labels, centroids = run_Kmeans(scores, clusters)

        # For K-means clustering, plot the centroid of each cluster
        # number = ['Cluster ' + str(i+1) for i in range(clusters)]
        # x = [coord[columns.index(t1)] for coord in centroids]
        # y = [coord[columns.index(t2)] for coord in centroids]
        # d3 = dict(index=number, x=x, y=y, color=COLORS[:clusters])

    # Run Spectral clustering
    elif alg == METHODS[1]:
        labels = run_SpectralClustering(scores, clusters)

    colors = [COLORS[x] for x in labels]
    data = dict(x=scores_dict[t1], y=scores_dict[t2], hashtag=words, colors=colors)

    return data


def run_Kmeans(data, clusters):
    estimator = KMeans(n_clusters=clusters, random_state=0).fit(data)
    return estimator.labels_, estimator.cluster_centers_


def run_SpectralClustering(data, clusters):
    estimator = SpectralClustering(n_clusters=clusters).fit(data)
    return estimator.labels_


# Read in USA Geolocated Twitter dataset
fpath = './data/USA-Geolocated-tweets/dashboard_x_usa_x_filter_nativeretweets.xlsx'
df = pd.read_excel(fpath, sheetname='Stream')
tweets = df['Tweet content']

# Extract hashtags from tweets and count their co-occurence
id2word, word2id = extract_hashtags(tweets, THRESHOLD)
co_occurence = count_cooccurence(tweets, word2id)
words = list(word2id.keys())
nWords = len(words)

# Set up position for the nodes
theta = 2 * np.pi / nWords
circ = [i * theta for i in range(nWords)]
coord_x = [np.cos(i) for i in circ]
coord_y = [np.sin(i) for i in circ]
#pos = np.random.rand(nWords, 2)

# Set up data source
s1 = ColumnDataSource(data=dict(x=coord_x, y=coord_y, hashtag=words))
s2 = ColumnDataSource(data=dict(x=[], y=[], hashtag=[], colors=[]))

# Draw the plots
hover1 = HoverTool(tooltips=[('Hashtag', '@hashtag')])
hover2 = HoverTool(tooltips=[('Hashtag', '@hashtag')])
p1 = figure(title="Hashtag co-occurence graph", tools=[hover1], **PLOT1_PARAM)
p2 = figure(tools='', **PLOT2_PARAM)
p2.circle('x', 'y', source=s2, size=20, color='colors', alpha=0.8)

# Draw the edges between the nodes
for (n1, n2), count in co_occurence.items():
    n1_x, n1_y = coord_x[n1], coord_y[n1]
    n2_x, n2_y = coord_x[n2], coord_y[n2]
    p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#949494")
scatter = p1.circle('x', 'y', source=s1, size=20)

# Add a hover tool to the co-occurence plot
hover1.renderers.append(scatter)
p2.add_tools(hover2)

# Set up figure parameters
p1.grid.visible = False
p1.axis.visible = False
p1.outline_line_color = None
p1.title.text_font_size = p2.title.text_font_size = '16px'

# Construct co-occurence gragh using networkx module
edges = [(pair[0], pair[1], weight)for pair, weight in co_occurence.items()]
G = nx.Graph()
G.add_nodes_from(range(nWords))
G.add_weighted_edges_from(edges)

# Compute the scores of each hashtag using PageRank and other centrality measures.
pr_score = nx.pagerank(G, weight='weight')
degree_score = nx.degree_centrality(G)
close_score = nx.closeness_centrality(G)
between_score = nx.betweenness_centrality(G, weight='weight')

scores_dict = dict()
scores_dict['PageRank'] = list(pr_score.values())
scores_dict['Degree centrality'] = list(degree_score.values())
scores_dict['Closeness centrality'] = list(close_score.values())
scores_dict['Betweenness centrality'] = list(between_score.values())
scores = pd.DataFrame(scores_dict).as_matrix()

# Set up widgets
x_ticker = Select(title='X Axis:', value='PageRank',
                  options=nix('Degree centrality', DEFAULT_TICKERS))
y_ticker = Select(title='Y Axis:', value='Degree centrality',
                  options=nix('PageRank', DEFAULT_TICKERS))
alg_ticker = Select(title='Clustering:', value='K-means', options=METHODS)
cluster_slider = Slider(title='Clusters', value=3, start=1, end=8, step=1)


def x_ticker_change(attrname, old, new):
    y_ticker.options = nix(new, DEFAULT_TICKERS)
    update()


def y_ticker_change(attrname, old, new):
    x_ticker.options = nix(new, DEFAULT_TICKERS)
    update()


def setting_change(attrname, old, new):
    update()


def update():
    t1, t2, alg = x_ticker.value, y_ticker.value, alg_ticker.value
    clusters = cluster_slider.value

    s2.data = get_data(t1, t2, alg, clusters)
    p2.xaxis.axis_label = t1
    p2.yaxis.axis_label = t2
    p2.title.text = 'Rank hashtags (%s vs. %s)' % (t1, t2)


x_ticker.on_change('value', x_ticker_change)
y_ticker.on_change('value', y_ticker_change)
alg_ticker.on_change('value', setting_change)
cluster_slider.on_change('value', setting_change)

# Set up layout
desc = Div(text=open('description.html').read(), width=580, height=180)
p2_widget = row(p2, widgetbox(x_ticker, y_ticker, alg_ticker, cluster_slider))
layout = column(desc, p1, p2_widget)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = 'USA Geolocated Twitter'
