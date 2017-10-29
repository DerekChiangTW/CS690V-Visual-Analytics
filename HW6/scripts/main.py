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
from bokeh.models.widgets import Select, Div
from sklearn.cluster import KMeans, SpectralClustering
from utils import get_tagCount, extract_hashtags, count_cooccurence

pd.options.mode.chained_assignment = None

threshold = 30
time_unit = ['Day', 'Week', 'Month']
p2_tools = 'pan,xbox_select,reset'
p1_params = {'plot_height': 350, 'plot_width': 350, 'toolbar_location': None}
p2_params = {'plot_height': 300, 'plot_width': 900,
             'x_axis_type': 'datetime', 'active_drag': "xbox_select"}


def get_data(time):
    """ time = ['Day'|'Week'|'Month']. """
    grouped = time_df.groupby(pd.TimeGrouper(freq=time[:1]))
    time_dict = {time_stamp: get_tagCount(texts.tolist()) for time_stamp, texts in grouped}
    return time_dict.keys(), time_dict.values()


# Read in dataset
fpath = './../data/costco/export_dashboard_cost_2016_06_15_12_24_55.xlsx'
df = pd.read_excel(fpath, sheetname='Stream')


# Preprocess the data
time_df = df['Tweet content']
time_df.index = pd.to_datetime(df['Date'] + ' ' + df['Hour'])
id2word, word2id = extract_hashtags(time_df, threshold)
co_occurence = count_cooccurence(time_df, word2id)
words = list(word2id.keys())
nWords = len(words)


# Set up position for the nodes
theta = 2 * np.pi / nWords
circ = [i * theta for i in range(nWords)]
coord_x = [np.cos(i) for i in circ]
coord_y = [np.sin(i) for i in circ]
color = ['#1F77B4'] * nWords


# Set up DataSource and figures
s1 = ColumnDataSource(data=dict(x=coord_x, y=coord_y, hashtag=words, color=color))
s2 = ColumnDataSource(data=dict(x=[], y=[], hashtags=[]))

hover1 = HoverTool(tooltips=[('Hashtag', '@hashtag')])
hover2 = HoverTool(tooltips=[('Num of Hashtag', '@y')], mode='vline')


# Draw the edges between the nodes
p1 = figure(title="Hashtag co-occurence graph", tools=[hover1], **p1_params)
for (n1, n2), count in co_occurence.items():
    n1_x, n1_y = coord_x[n1], coord_y[n1]
    n2_x, n2_y = coord_x[n2], coord_y[n2]
    p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#949494", line_width=2)
scatter = p1.circle('x', 'y', source=s1, color='color', size=20)
hover1.renderers.append(scatter)

p2 = figure(title="Hashtag count", tools=p2_tools, **p2_params)
p2.line('x', 'y', source=s2, selection_color="orange", line_width=3)
p2.circle('x', 'y', size=6, source=s2, color=None, selection_color="orange")
p2.add_tools(hover2)

# Set up figure parameters
p1.grid.visible = False
p1.axis.visible = False
p1.outline_line_color = None
p1.title.text_font_size = p2.title.text_font_size = '16px'


# Set up widgets
time_ticker = Select(title='Time:', value='Week', options=time_unit)


def time_change(attrname, old, new):
    update()


def selection_change(attrname, old, new):
    # pass
    selected = s2.selected['1d']['indices']

    hashtags = []
    if selected:
        data = s2.data['hashtags']
        for index in selected:
            hashtags += data[index]
        hashtags = set(hashtags)

    new_color = ['#1F77B4'] * nWords
    for t in hashtags:
        if t in word2id.keys():
            new_color[word2id[t]] = '#ae254a'
    s1.data = dict(x=coord_x, y=coord_y, hashtag=words, color=new_color)


def update():
    t1 = time_ticker.value

    time_stamps, tag_dicts = get_data(t1)
    nTag_count = [sum(tag_dict.values()) for tag_dict in tag_dicts]
    nTag_list = [list(tag_dict.keys()) for tag_dict in tag_dicts]

    s2.data = dict(x=list(time_stamps), y=nTag_count, hashtags=nTag_list)


time_ticker.on_change('value', time_change)
s2.on_change('selected', selection_change)

layout = column(p1, time_ticker, p2)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = 'Costco Corp. Twitter'
