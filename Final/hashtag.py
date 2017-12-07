#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from random import shuffle
from bokeh.io import curdoc
from wordcloud import WordCloud
from collections import Counter
from itertools import combinations
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Select, PreText
from scripts.sentiment import posSent, negSent, sentScore, getSentWords
from scripts.utils import extract_hashtags, run_pagerank

targetNum = 25
pd.options.mode.chained_assignment = None
period = ['3Min', '5Min', '10Min', '15Min', '30Min']
# wc_params = {'plot_height': 300, 'plot_width': 400, 'toolbar_location': None}
p1_params = {'plot_height': 450, 'plot_width': 450, 'toolbar_location': None}
tp_params = {'plot_height': 300, 'plot_width': 800, 'x_axis_type': 'datetime', 'y_axis_label': 'Count',
             'active_drag': "xbox_select", 'tools': 'pan,xbox_select,reset'}


def get_data(period, target_tag):
    """ Get the data for the time-series plot. """

    # Split the hashtags based on timestamps
    grouped = df['hashtags'].groupby(pd.TimeGrouper(freq=period))
    time_stamps, partial_hashtags = zip(*grouped)

    # Get the data for total count
    # tw_count = [len(x) for x in partial_hashtags]
    tag_count = [len(sum(x.values, [])) for x in partial_hashtags]
    tp1_data = dict(time=time_stamps, nTags=tag_count)

    # Get the data for the specified hashtag
    target_count = [Counter(sum(x.values, []))[target_tag] for x in partial_hashtags]
    tp2_data = dict(time=time_stamps, count=target_count)
    return tp1_data, tp2_data


def img2bokeh(input_image):
    xdim, ydim = input_image.size
    input_image = input_image.resize((xdim, ydim))
    input_image = input_image.convert("RGBA")
    img = np.empty((ydim, xdim), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
    view[:, :, :] = np.flipud(np.asarray(input_image))
    dim = max(xdim, ydim)
    return view, dim


# Read in dataset
fpath = "./data/VAST-2014-MC3/1700-1830.csv"
origin_df = pd.read_csv(fpath)

# Extract hashtags from tweets and perform sentiment analysis
df = pd.DataFrame(
    {'tweet': origin_df['message'].values,
     'hashtags': [extract_hashtags(tweet) for tweet in origin_df['message']],
     'sentScore': [sentScore(tweet) for tweet in origin_df['message']],
     'sentWords': [getSentWords(tweet) for tweet in origin_df['message']]},
    index=pd.to_datetime(origin_df['date(yyyyMMddHHmmss)'], format='%Y%m%d%H%M%S'))

# Index unique hashtags
unique_tags = sorted(set(sum([tag for tag in df['hashtags']], [])))

# Set up DataSource
p1_source = ColumnDataSource(data=dict(x=[], y=[], tag=[], color=[]))
tp1_source = ColumnDataSource(data=dict(time=[], nTags=[]))
tp2_source = ColumnDataSource(data=dict(time=[], count=[]))

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ---------------- CO-OCCURENCE GRAPH ------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
top_tags = run_pagerank(df['hashtags'], unique_tags, targetNum)
shuffle(top_tags)
id2tag = {i: tag for i, tag in enumerate(top_tags)}
tag2id = {tag: i for i, tag in id2tag.items()}

edges = dict()
for tag_list in df['hashtags']:
    indices = [tag2id[tag] for tag in tag_list if tag in top_tags]
    for pair in combinations(indices, 2):
        edges[pair] = edges.get(pair, 0) + 1

# Construct co-occurence graph and set up position for the nodes
radius = 4
theta = 2 * np.pi / targetNum
circ = [i * theta for i in range(targetNum)]
pos_x = [radius * np.cos(i) for i in circ]
pos_y = [radius * np.sin(i) for i in circ]
colors = ['#1F77B4'] * targetNum

# Plot the co-occcurrence graph
p1_source.data = dict(x=pos_x, y=pos_y, tag=top_tags, color=colors)
p1_hover = HoverTool(tooltips=[('Hashtag', '@tag')])
p1 = figure(title="Hashtag co-occurence graph", tools=[p1_hover], **p1_params)
for (n1, n2), count in edges.items():
    n1_x, n1_y = pos_x[n1], pos_y[n1]
    n2_x, n2_y = pos_x[n2], pos_y[n2]
    width = 3
    if count > 5 and count <= 10:
        width = 5
    elif count > 10:
        width = 7
    p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#aeaeae", line_width=width)
scatter = p1.circle('x', 'y', source=p1_source, color='color', size=26)
p1_hover.renderers.append(scatter)
p1.grid.visible = False
p1.axis.visible = False
p1.outline_line_color = None

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ---------------- TOTAL HASHTAG COUNT -----------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
tp1 = figure(title="Distribution of hashtag count", **tp_params)
tp1.line('time', 'nTags', source=tp1_source, selection_color="orange", line_width=3)
tp1.circle('time', 'nTags', size=6, source=tp1_source, fill_color="white", selection_color="orange")
tp1_hover = HoverTool(
    tooltips=[
        ("Time period", "@time{%H:%M}"),
        ("# of hashtags", "@nTags")],
    formatters={'time': 'datetime'},
    mode='vline'
)
tp1.add_tools(tp1_hover)


# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------
# # ---------------- WordCloud ---------------------------------------------
# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------
# wordcloud = WordCloud(background_color="white").generate("".join(sum([tag_list for tag_list in df['hashtags']], [])))
# p_image, dim = img2bokeh(wordcloud.to_image())
# p_cloud = figure(x_range=(0, dim), y_range=(0, dim), title="Real-time wordcloud", **wc_params)
# p_cloud.xaxis.visible = False
# p_cloud.yaxis.visible = False
# p_cloud.image_rgba(image=[p_image], x=0, y=0, dw=dim, dh=dim)


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ---------------- INDIVIDUAL HASHTAG GRAPH ------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
tp2 = figure(**tp_params)
tp2.line('time', 'count', source=tp2_source, color='#007380', selection_color="orange", line_width=3)
tp2.circle('time', 'count', size=6, source=tp2_source, fill_color="white", selection_color="orange")
tp2_hover = HoverTool(
    tooltips=[
        ("Time period", "@time{%H:%M}"),
        ("Count", '@count')],
    formatters={'time': 'datetime'},
    mode='vline'
)
tp2.add_tools(tp2_hover)
tweet_area = PreText(text='', width=1200, height=800)
# sent_tweet_area = PreText(text='', width=1200, height=800)


# Set up selection widgets
time_ticker = Select(title='Period:', value='3Min', options=period)
hashtag_ticker = Select(title='Hashtag:', value='#kronosstar', options=unique_tags)


def update_tweet(attrname, old, new):
    selected = tp2_source.selected['1d']['indices']
    t1, t2 = time_ticker.value, hashtag_ticker.value

    tweet_area.text = '      Date time      |                Tweet       \n'
    tweet_area.text += '=======================================================================================\n'
    time_stamps, df_list = zip(*df.groupby(pd.TimeGrouper(freq=t1)))
    for i in selected:
        for time, r in df_list[i].iterrows():
            if t2 in r['hashtags']:
                line = str(time) + '  |  ' + r['tweet'] + '\n'
                tweet_area.text += line


def update():
    t1, t2 = time_ticker.value, hashtag_ticker.value
    tp1_source.data, tp2_source.data = get_data(t1, t2)

    tp1.xaxis.axis_label = tp2.xaxis.axis_label = "Time (" + t1 + ")"
    tp2.title.text = "Distribution of Hashtag: {}".format(t2)

    # # update wordcloud
    # wordcloud = WordCloud(background_color="white").generate(" ".join(tweets))
    # p_image, dim = img2bokeh(wordcloud.to_image())
    # p_cloud.image_rgba(image=[p_image], x=0, y=0, dw=dim, dh=dim)


time_ticker.on_change('value', lambda attr, old, new: update())
hashtag_ticker.on_change('value', lambda attr, old, new: update())
tp2_source.on_change('selected', update_tweet)

# Set up layouts
time_widget = column(row(time_ticker, hashtag_ticker), tp1, tp2)
layout = column(row(time_widget, p1), tweet_area)

# Initialize
update()

# curdoc().add_root(column(plot, sent_tweet_area))
curdoc().add_root(layout)
curdoc().title = 'VAST Challenge, 2014 MC3'
