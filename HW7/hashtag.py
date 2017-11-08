#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from collections import Counter
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTicker, FixedTicker, Range1d
from bokeh.models.widgets import Select, DataTable, TableColumn, PreText
from scripts.utils import extract_hashtags

pd.options.mode.chained_assignment = None

threshold = 30
period = ['3Min', '5Min', '10Min', '15Min', '30Min', 'H']
p1_params = {'plot_height': 400, 'plot_width': 400, 'toolbar_location': None}
tp_params = {'plot_height': 250, 'plot_width': 800, 'x_axis_type': 'datetime',
             'active_drag': "xbox_select", 'tools': 'pan,xbox_select,reset'}


def get_data(period, target_tag):
    """ Get the data for the time-series plot. """

    # Split the hashtags based on timestamps
    grouped = hashtags.groupby(pd.TimeGrouper(freq=period))
    time_stamps, partial_hashtags = zip(*grouped)

    # Get the data for total count
    tw_count = [len(x) for x in partial_hashtags]
    tag_count = [len(sum(x.values, [])) for x in partial_hashtags]
    tp1_data = dict(time=time_stamps, nTweets=tw_count, nTags=tag_count)

    # Get the data for the specified hashtag
    target_count = [Counter(sum(x.values, []))[target_tag] for x in partial_hashtags]
    tp2_data = dict(time=time_stamps, count=target_count)

    return tp1_data, tp2_data


# Read in dataset
fpath = './data/VAST-2014-MC3/1700-1830.csv'
raw_df = pd.read_csv(fpath)

# Extract hashtags
df = pd.DataFrame({'tweet': raw_df['message'],
                   'hashtags': [extract_hashtags(tweet) for tweet in raw_df['message']]})
date_time = pd.to_datetime(raw_df['date(yyyyMMddHHmmss)'], format='%Y%m%d%H%M%S')
df = df.rename(index=dict(zip(range(len(date_time)), date_time)))


hashtags = df['hashtags']
unique_hashtags = sorted(set(sum([x for x in hashtags], [])))
id2tag = {i: tag for i, tag in enumerate(unique_hashtags)}
tag2id = {tag: i for i, tag in id2tag.items()}

# # Get all hashtags from tweets and index them
# top_hashtags = extract_hashtags(df['Tweet content'], threshold)
# id2word = {i: tag for i, tag in enumerate(sorted(top_hashtags))}
# word2id = {tag: i for i, tag in id2word.items()}
# co_occurence = count_cooccurence(tag_table, word2id)
# Tags = list(word2id.keys())
# nTags = len(Tags)
# colors = ['#1F77B4'] * nTags

# # Construct co-occurence graph and set up position for the nodes
# radius = 4
# theta = 2 * np.pi / nTags
# circ = [i * theta for i in range(nTags)]
# pos_x = [radius * np.cos(i) for i in circ]
# pos_y = [radius * np.sin(i) for i in circ]

# # Set up DataSource and figures
# s1 = ColumnDataSource(data=dict(x=pos_x, y=pos_y, text=Tags, color=colors))
# tp1_source = ColumnDataSource(data=dict(x=[], y=[], hashtags=[]))
# tweet_source = ColumnDataSource(data=dict(time=[], tweet=[]))
tp1_source = ColumnDataSource(data=dict(time=[], nTweets=[], nTags=[]))
tp2_source = ColumnDataSource(data=dict(time=[], count=[]))
# hover1 = HoverTool(tooltips=[('Hashtag', '@text')])
tp1_hover = HoverTool(
    tooltips=[
        ("Time period", "@time{%H:%M}"),
        ("# of tweets", "@nTweets"),
        ("# of hashtags", "@nTags")
    ],
    formatters={'time': 'datetime'},
    mode='vline'
)
tp2_hover = HoverTool(tooltips=[("Count", '@count')], mode='vline')


# # Draw the co-occurence graph
# p1 = figure(title="Hashtag co-occurence graph", tools=[hover1], **p1_params)
# for (n1, n2), count in co_occurence.items():
#     n1_x, n1_y = pos_x[n1], pos_y[n1]
#     n2_x, n2_y = pos_x[n2], pos_y[n2]

#     width = 2
#     if count > 5 and count <= 10:
#         width = 4
#     elif count > 10:
#         width = 6
#     p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#aeaeae", line_width=width)
# scatter = p1.circle('x', 'y', source=s1, color='color', size=24)
# hover1.renderers.append(scatter)

tp1 = figure(title="Distribution of total hashtag count", **tp_params)
tp1.line('time', 'nTags', source=tp1_source, selection_color="orange", line_width=3)
tp1.circle('time', 'nTags', size=6, source=tp1_source, fill_color="white", selection_color="orange")
tp1.add_tools(tp1_hover)

tp2 = figure(**tp_params)
tp2.line('time', 'count', source=tp2_source, color='#007380', selection_color="orange", line_width=3)
tp2.circle('time', 'count', size=6, source=tp2_source, fill_color="white", selection_color="orange")
tp2.add_tools(tp2_hover)

tweet_area = PreText(text='', width=1200, height=800)

# # Set up figure parameters
# p1.grid.visible = False
# p1.axis.visible = False
# p1.outline_line_color = None
tp1.yaxis.axis_label = tp2.yaxis.axis_label = 'Count'
tp1.title.text_font_size = tp2.title.text_font_size = '14px'

# Set up selection widgets
time_ticker = Select(title='Period:', value='10Min', options=period)
hashtag_ticker = Select(title='Hashtag:', value='#KronosStar', options=unique_hashtags)


def data_change(attrname, old, new):
    update()


def update_tweet(attrname, old, new):
    selected = tp2_source.selected['1d']['indices']
    t1, t2 = time_ticker.value, hashtag_ticker.value

    tweet_area.text = '      Date time      ||                Tweet       \n'
    tweet_area.text += '===============================================================================\n'
    time_stamps, partial_df = zip(*df.groupby(pd.TimeGrouper(freq=t1)))
    for i in selected:
        for idx, r in partial_df[i].iterrows():
            if t2 in r['hashtags']:
                line = str(idx) + '  ||  ' + r['tweet'] + '\n'
                tweet_area.text += line


def update():
    t1, t2 = time_ticker.value, hashtag_ticker.value
    tp1_source.data, tp2_source.data = get_data(t1, t2)

    tp1.xaxis.axis_label = tp2.xaxis.axis_label = "Time (" + t1 + ")"
    tp2.title.text = "Distribution of Hashtag: {}".format(t2)

    # tp1.xaxis.formatter = DatetimeTickFormatter(
    #     hourmin=["%H:%M"],
    #     hours=["%Hh', '%H:%M"])
    # tp1.xaxis[0].ticker = DatetimeTicker(tickers=time_stamps)
    # time_stamps = [x.to_pydatetime() for x in time_stamps]
    # tp1.y_range = Range1d(0, 1000)
    # tp1.xaxis[0].ticker = FixedTicker(ticks=time_stamps)


time_ticker.on_change('value', data_change)
hashtag_ticker.on_change('value', data_change)
tp2_source.on_change('selected', update_tweet)


time_widget = column(row(time_ticker, hashtag_ticker), tp1, tp2)
layout = column(time_widget, tweet_area)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = 'VAST Challenge, 2014 MC3'

# def selection_change(attrname, old, new):
#     selected = tp1_source.selected['1d']['indices']

#     hashtags = []
#     if selected:
#         data = tp1_source.data['hashtags']
#         for index in selected:
#             hashtags += data[index]
#         hashtags = set(hashtags)

#     new_color = ['#1F77B4'] * nTags
#     for t in hashtags:
#         if t in word2id.keys():
#             new_color[word2id[t]] = '#ae254a'
#     s1.data = dict(x=pos_x, y=pos_y, text=Tags, color=new_color)


# def update():
#     t1, t2 = time_ticker.value, hashtag_ticker.value

#     time_stamps, tag_dicts = get_data(t1)
#     nTag_count = [sum(tag_dict.values()) for tag_dict in tag_dicts]
#     nTag_list = [list(tag_dict.keys()) for tag_dict in tag_dicts]

#     t_count = list()
#     for tag_dict in tag_dicts:
#         if t2 in tag_dict:
#             t_count.append(tag_dict[t2])
#         else:
#             t_count.append(0)

#     tp1_source.data = dict(x=time_stamps, y=nTag_count, hashtags=nTag_list)
#     s3.data = dict(x=time_stamps, y=t_count)

# columns = [
#     TableColumn(field="time", title="Date time"),
#     TableColumn(field="tweet", title="Tweet")
# ]
# data_table = DataTable(source=tweet_source, columns=columns, width=800)

# def table_change(attrname, old, new):
#     selected = tp2_source.selected['1d']['indices']
#     t1, t2 = time_ticker.value, hashtag_ticker.value

#     time_list, tweet_list = [], []
#     time_stamps, partial_df = zip(*df.groupby(pd.TimeGrouper(freq=t1)))
#     for i in selected:
#         print(time_stamps[i])
#         for idx, r in partial_df[i].iterrows():
#             if t2 in r['hashtags']:
#                 time_list.append(idx)
#                 tweet_list.append(r['tweet'])
#     tweet_source.data = dict(time=time_list, tweet=tweet_list)
