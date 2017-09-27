#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import pandas as pd
from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Slider, NumeralTickFormatter, HoverTool
)
from bokeh.layouts import column, row, widgetbox
from bokeh.models.widgets import (
    Select, Div, Panel, Tabs, NumberFormatter
)
from sklearn.cluster import KMeans, SpectralClustering


def nix(val, lst):
    return [x for x in lst if x != val]

def get_data(t1, t2, alg, reg, clusters):
    """ Get the data according to user's settings.

    Args:
        t1: the selected column for x axis
        t2: the selected column for y axis
        alg: the clustering algorithm
        reg: the region for filtered plot
        clusters: the number of clusters for the clustering algorithm

    """
    
    # Run K-means clustering
    if alg == METHODS[0]:
        labels, centroids = run_Kmeans(data, clusters)

        # For K-means clustering, plot the centroid of each cluster
        number = ['Cluster ' + str(i+1) for i in range(clusters)]
        x = [coord[columns.index(t1)] for coord in centroids]
        y = [coord[columns.index(t2)] for coord in centroids]
        d3 = dict(index=number, x=x, y=y, color=COLORS[:clusters])
        
    # Run Spectral clustering
    elif alg == METHODS[1]:
        # Run the normalized data for the affinity matrix
        labels = run_SpectralClustering(data_norm, clusters)
        d3 = dict(index=[], x=[], y=[], color=[])

    indices = list(df.index)
    colors = [COLORS[x] for x in labels]
    d1 = dict(index=indices, x=df[t1], y=df[t2], color=colors)

    region_df = df.loc[lambda df: df.Region == int(reg), :]
    region_indices = list(region_df.index)
    region_colors = [colors[x] for x in region_indices]
    d2 = dict(index=region_indices, x=region_df[t1], y=region_df[t2], color=region_colors)

    return d1, d2, d3

def run_Kmeans(data, clusters):
    estimator = KMeans(n_clusters=clusters, random_state=0).fit(data)
    return estimator.labels_, estimator.cluster_centers_

def run_SpectralClustering(data, clusters):
    estimator = SpectralClustering(n_clusters=clusters).fit(data)
    return estimator.labels_


# Read in dataset
df = pd.read_csv(join(dirname(__file__), 'data/Wholesale customers data.csv'))
columns = sorted(df.columns[2:])
data = df[columns].as_matrix()

# Normalize each column (for Spectral Clustering)
df_norm = (df - df.min()) / (df.max() - df.min())
data_norm = df_norm[columns].as_matrix()

# Set the DataSource for the plots
s1 = ColumnDataSource(data=dict(index=[], x=[], y=[], color=[]))
s2 = ColumnDataSource(data=dict(index=[], x=[], y=[], color=[]))
s3 = ColumnDataSource(data=dict(index=[], x=[], y=[], color=[]))


# Default settings
DEFAULT_TICKERS = columns
METHODS = ['K-means', 'Spectral']
DEFALUT_TOOLS = ['pan', 'box_zoom', 'reset']
COLORS = ['#ae254a', '#007380', '#4364ae', '#f9d500',
          '#ff7256', '#800080', '#0e2f44', '#f442cb']
PLOT_PARAM = {'plot_height': 400, 'plot_width': 600, 'responsive': True,
              'toolbar_location': 'above', 'tools': DEFALUT_TOOLS}

# Draw an interactive scatter plot to show the data distribution
p1 = figure(**PLOT_PARAM)
p1.circle('x', 'y', source=s1, size=12, color='color', alpha=0.6)
p1.circle_x('x', 'y', source=s3, size=20, color='color', fill_alpha=1.0, line_color='black', line_width=2)
p1.title.text_font_size='16px'
p1.xaxis.formatter=p1.yaxis.formatter=NumeralTickFormatter(format='$ 0,0')

p2 = figure(x_range=p1.x_range, y_range=p1.y_range, **PLOT_PARAM)
p2.circle('x', 'y', source=s2, size=12, color='color', alpha=0.6)
p2.title.text_font_size='16px'
p2.xaxis.formatter=p2.yaxis.formatter=NumeralTickFormatter(format='$ 0,0')

# Add a hover tool to the scatter plot
hover = HoverTool(
    tooltips=[
        ('Index: ', '@index'),
        ('x: ', '@x{$ 0,0}'),
        ('y: ', '@y{$ 0,0}')
    ]
)
p1.add_tools(hover)
p2.add_tools(hover)


# Set up widgets
x_ticker = Select(title='X Axis:', value='Milk', options=nix('Fresh', DEFAULT_TICKERS))
y_ticker = Select(title='Y Axis:', value='Fresh', options=nix('Milk', DEFAULT_TICKERS))
alg_ticker = Select(title='Clustering:', value='K-means', options=METHODS)
reg_ticker = Select(title='Region:', value='1', options=['1', '2', '3'])
cluster_slider = Slider(title='Clusters', value=4, start=1, end=8, step=1)


# Set up callbacks
def x_ticker_change(attrname, old, new):
    y_ticker.options = nix(new, DEFAULT_TICKERS)
    update()

def y_ticker_change(attrname, old, new):
    x_ticker.options = nix(new, DEFAULT_TICKERS)
    update()

def setting_change(attrname, old, new):
    update()

def update():
    t1, t2, t3, t4 = x_ticker.value, y_ticker.value, alg_ticker.value, reg_ticker.value
    clusters = cluster_slider.value

    s1.data, s2.data, s3.data = get_data(t1, t2, t3, t4, clusters)
    p1.xaxis.axis_label = p2.xaxis.axis_label = t1 + ' (m.u.)'
    p1.yaxis.axis_label = p2.yaxis.axis_label = t2 + ' (m.u.)'
    p1.title.text = '%s vs. %s' % (t1, t2)
    p2.title.text = 'Region {} only'.format(t4)


x_ticker.on_change('value', x_ticker_change)
y_ticker.on_change('value', y_ticker_change)
alg_ticker.on_change('value', setting_change)
reg_ticker.on_change('value', setting_change)
cluster_slider.on_change('value', setting_change)


# Set up layout
desc = Div(text=open(join(dirname(__file__), 'description.html')).read(), width=700, height=120)
tickers = widgetbox(x_ticker, y_ticker, alg_ticker)
p1_widget = row(p1, column(tickers, cluster_slider))
p2_widget = row(p2, reg_ticker)
scatter_widget = column(p1_widget, p2_widget)
tab1 = Panel(child=scatter_widget, title='Scatter')
tabs = Tabs(tabs=[tab1])
layout = column(desc, tabs)


# Initialize
update()

curdoc().add_root(layout)
curdoc().title = 'Wholesale Customers'
