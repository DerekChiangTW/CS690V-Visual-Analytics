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
from scripts.utils import extract_hashtags, count_cooccurence

pd.options.mode.chained_assignment = None

threshold = 30
time_unit = ['Day', 'Week', 'Month']
p1_params = {'plot_height': 400, 'plot_width': 400, 'toolbar_location': None}
p2_params = {'plot_height': 250, 'plot_width': 800, 'x_axis_type': 'datetime',
             'active_drag': "xbox_select", 'tools': 'pan,xbox_select,reset'}
p3_params = {'plot_height': 250, 'plot_width': 800, 'x_axis_type': 'datetime',
             'tools': '', 'toolbar_location': None}


def get_data(time_unit):
    """ time_unit = ['Day'|'Week'|'Month']. """
    grouped = tag_table.groupby(pd.TimeGrouper(freq=time_unit[:1]))
    time_stamps = []
    hash_lists = []
    for time_stamp, hash_dicts in grouped:
        group_dict = dict()
        for hash_dict in hash_dicts:
            for k, v in hash_dict.items():
                group_dict[k] = group_dict.get(k, 0) + 1

        time_stamps.append(time_stamp)
        hash_lists.append(group_dict)
    return time_stamps, hash_lists


# Read in dataset
fpath = './data/costco/export_dashboard_cost_2016_06_15_12_24_55.xlsx'
df = pd.read_excel(fpath, sheetname='Stream')

# Preprocess the data
tag_table = pd.Series([extract_hashtags(tweet) for tweet in df['Tweet content']])
tag_table.index = pd.to_datetime(df['Date'] + ' ' + df['Hour'])

# Get all hashtags from tweets and index them
top_hashtags = extract_hashtags(df['Tweet content'], threshold)
id2word = {i: tag for i, tag in enumerate(sorted(top_hashtags))}
word2id = {tag: i for i, tag in id2word.items()}
co_occurence = count_cooccurence(tag_table, word2id)
Tags = list(word2id.keys())
nTags = len(Tags)
colors = ['#1F77B4'] * nTags

# Construct co-occurence graph and set up position for the nodes
radius = 4
theta = 2 * np.pi / nTags
circ = [i * theta for i in range(nTags)]
pos_x = [radius * np.cos(i) for i in circ]
pos_y = [radius * np.sin(i) for i in circ]

# Set up DataSource and figures
s1 = ColumnDataSource(data=dict(x=pos_x, y=pos_y, text=Tags, color=colors))
s2 = ColumnDataSource(data=dict(x=[], y=[], hashtags=[]))
s3 = ColumnDataSource(data=dict(x=[], y=[]))
# s3 = ColumnDataSource
hover1 = HoverTool(tooltips=[('Hashtag', '@text')])
hover2 = HoverTool(tooltips=[('Count of Hashtags', '@y')], mode='vline')
hover3 = HoverTool(tooltips=[('Count of Hashtags', '@y')], mode='vline')

# Draw the co-occurence graph
p1 = figure(title="Hashtag co-occurence graph", tools=[hover1], **p1_params)
for (n1, n2), count in co_occurence.items():
    n1_x, n1_y = pos_x[n1], pos_y[n1]
    n2_x, n2_y = pos_x[n2], pos_y[n2]

    width = 2
    if count > 5 and count <= 10:
        width = 4
    elif count > 10:
        width = 6
    p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#aeaeae", line_width=width)
scatter = p1.circle('x', 'y', source=s1, color='color', size=24)
hover1.renderers.append(scatter)

p2 = figure(title="Distribution of total hashtag count", **p2_params)
p2.line('x', 'y', source=s2, selection_color="orange", line_width=3)
p2.circle('x', 'y', size=6, source=s2, color=None, selection_color="orange")
p2.add_tools(hover2)

p3 = figure(title="Distribution", **p3_params)
p3.line('x', 'y', source=s3, color='#007380', selection_color="orange", line_width=3)
p3.circle('x', 'y', size=6, source=s3, color=None, selection_color="orange")
p3.add_tools(hover3)

# Set up figure parameters
p1.grid.visible = False
p1.axis.visible = False
p1.outline_line_color = None
p2.yaxis.axis_label = p3.yaxis.axis_label = 'Count'
p1.title.text_font_size = p2.title.text_font_size = p3.title.text_font_size = '18px'

# Set up widgets
time_ticker = Select(title='Time Unit:', value='Month', options=time_unit)
hashtag_ticker = Select(title='Hashtag', value=Tags[0], options=Tags)


def data_change(attrname, old, new):
    update()


def selection_change(attrname, old, new):
    selected = s2.selected['1d']['indices']

    hashtags = []
    if selected:
        data = s2.data['hashtags']
        for index in selected:
            hashtags += data[index]
        hashtags = set(hashtags)

    new_color = ['#1F77B4'] * nTags
    for t in hashtags:
        if t in word2id.keys():
            new_color[word2id[t]] = '#ae254a'
    s1.data = dict(x=pos_x, y=pos_y, text=Tags, color=new_color)


def update():
    t1, t2 = time_ticker.value, hashtag_ticker.value

    time_stamps, tag_dicts = get_data(t1)
    nTag_count = [sum(tag_dict.values()) for tag_dict in tag_dicts]
    nTag_list = [list(tag_dict.keys()) for tag_dict in tag_dicts]

    t_count = list()
    for tag_dict in tag_dicts:
        if t2 in tag_dict:
            t_count.append(tag_dict[t2])
        else:
            t_count.append(0)

    s2.data = dict(x=time_stamps, y=nTag_count, hashtags=nTag_list)
    s3.data = dict(x=time_stamps, y=t_count)

    p2.xaxis.axis_label = p3.xaxis.axis_label = 'Date(' + t1 + ')'
    p3.title.text = "Distribution of Hashtag: {}".format(t2)


time_ticker.on_change('value', data_change)
hashtag_ticker.on_change('value', data_change)
s2.on_change('selected', selection_change)

time_widget = column(row(time_ticker, hashtag_ticker), p2, p3)
layout = row(p1, time_widget)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = 'Costco Corp. Twitter'
