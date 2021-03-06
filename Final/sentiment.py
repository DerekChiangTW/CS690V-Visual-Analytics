#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from wordcloud import WordCloud
from collections import Counter
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTicker, FactorRange
from bokeh.models.widgets import Select, DataTable, TableColumn, PreText
from scripts.sentiment import posSent, negSent, sentScore, getSentWords
from scripts.utils import extract_hashtags

# selected_Tags = 25
pd.options.mode.chained_assignment = None
# period = ['3Min', '5Min', '10Min', '15Min', '30Min']
# p1_params = {'plot_height': 500, 'plot_width': 500, 'toolbar_location': None}
# tp_params = {'plot_height': 250, 'plot_width': 800, 'x_axis_type': 'datetime',
# 'active_drag': "xbox_select", 'tools': 'pan,xbox_select,reset'}
sent_params = {'plot_height': 400, 'plot_width': 1000, 'tools': 'tap', 'toolbar_location': None}


# def get_data(period, target_tag):
#     """ Get the data for the time-series plot. """

#     # Split the hashtags based on timestamps
#     grouped = df['hashtags'].groupby(pd.TimeGrouper(freq=period))
#     time_stamps, partial_hashtags = zip(*grouped)

#     # Get the data for total count
#     tw_count = [len(x) for x in partial_hashtags]
#     tag_count = [len(sum(x.values, [])) for x in partial_hashtags]
#     tp1_data = dict(time=time_stamps, nTweets=tw_count, nTags=tag_count)

#     # Get the data for the specified hashtag
#     target_count = [Counter(sum(x.values, []))[target_tag] for x in partial_hashtags]
#     tp2_data = dict(time=time_stamps, count=target_count)
#     return tp1_data, tp2_data


def get_sent_data(df):
    freq = '3Min'
    grouped = df.groupby(pd.TimeGrouper(freq))
    time_stamps, part_dfs = zip(*grouped)

    pos, neg = [], []
    posCount, negCount = [], []
    for part_df in part_dfs:
        pos_tweets, neg_tweets = [], []
        pos_count = neg_count = 0
        for r in part_df.itertuples():
            score, tweet = r[2], r[4]
            if score > 0:
                pos_tweets.append(tweet)
                pos_count += 1
            elif score < 0:
                neg_tweets.append(tweet)
                neg_count -= 1
        pos.append(pos_tweets)
        neg.append(neg_tweets)
        posCount.append(pos_count)
        negCount.append(neg_count)

    time_labels = [str(ts)[-8:-3] for ts in time_stamps]
    sent_source = ColumnDataSource(
        data=dict(ts=time_labels, pos_tweets=pos, neg_tweets=neg,
                  pos_counts=posCount, neg_counts=negCount))
    return time_labels, sent_source

# def get_sent_count(sentiment):
#     freq = '3Min'
#     grouped = sentiment.groupby(pd.TimeGrouper(freq))
#     time_stamps, part_senti = zip(*grouped)

#     pos_senti, neg_senti = [], []
#     for senti in part_senti:
#         pos = neg = 0
#         for s in senti:
#             if s > 0:
#                 pos += 1
#             elif s < 0:
#                 neg -= 1
#         pos_senti.append(pos)
#         neg_senti.append(neg)
#     return time_stamps, pos_senti, neg_senti


# def img2bokeh(input_image):
#     xdim, ydim = input_image.size
#     input_image = input_image.resize((xdim, ydim))
#     input_image = input_image.convert("RGBA")
#     img = np.empty((ydim, xdim), dtype=np.uint32)
#     view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
#     view[:, :, :] = np.flipud(np.asarray(input_image))
#     dim = max(xdim, ydim)
#     return view, dim


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

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ---------------- SENTIMENT GRAPH ---------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
time_labels, sent_source = get_sent_data(df)
# time_stamps, pos_senti, neg_senti = get_sent_count(df['sentScore'])
# time_labels = get_TimeLabel(time_stamps)
plot = figure(x_range=time_labels, **sent_params)
plot.vbar(x='ts', width=0.7, bottom=0, top='pos_counts', source=sent_source, color="#4668a5", legend='Positive')
plot.vbar(x='ts', width=0.7, bottom=0, top='neg_counts', source=sent_source, color="#E35559", legend='Negative')
plot.xgrid.grid_line_color = None
plot.xaxis.major_label_orientation = 0.75


# # Get the data for total count
# tw_count = [len(x) for x in partial_hashtags]
# tag_count = [len(sum(x.values, [])) for x in partial_hashtags]
# tp1_data = dict(time=time_stamps, nTweets=tw_count, nTags=tag_count)


# # Index hashtags
# unique_hashtags = sorted(set(sum([tag for tag in df['hashtags']], [])))
# id2tag = {i: tag for i, tag in enumerate(unique_hashtags)}
# tag2id = {tag: i for i, tag in id2tag.items()}

# # Count the occurence and co-occurence of top hashtags
# tag_count = Counter(sum([tag for tag in df['hashtags']], []))
# top_tags = sorted([tag for tag, count in tag_count.most_common(selected_Tags)])
# co_occurence = count_cooccurence(df['hashtags'], top_tags)
# colors = ['#1F77B4'] * selected_Tags

# # Wordcloud
# wordcloud = WordCloud(background_color="white").generate(" ".join(df['tweet']))
# p_image, dim = img2bokeh(wordcloud.to_image())
# p_cloud = figure(x_range=(0, dim), y_range=(0, dim), plot_width=400, plot_height=300, title="Real-time wordcloud")
# p_cloud.xaxis.visible = False
# p_cloud.yaxis.visible = False
# p_cloud.image_rgba(image=[p_image], x=0, y=0, dw=dim, dh=dim)

# # Set up DataSource
# p1_source = ColumnDataSource(data=dict(x=pos_x, y=pos_y, tag=top_tags, color=colors))
# tp1_source = ColumnDataSource(data=dict(time=[], nTweets=[], nTags=[]))
# tp2_source = ColumnDataSource(data=dict(time=[], count=[]))
# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------
# # ---------------- CO-OCCURENCE GRAPH ------------------------------------
# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------

# # Construct co-occurence graph and set up position for the nodes
# radius = 5
# theta = 2 * np.pi / selected_Tags
# circ = [i * theta for i in range(selected_Tags)]
# pos_x = [radius * np.cos(i) for i in circ]
# pos_y = [radius * np.sin(i) for i in circ]

# p1_hover = HoverTool(tooltips=[('Hashtag', '@tag')])
# p1 = figure(title="Hashtag co-occurence graph", tools=[p1_hover], **p1_params)
# for (n1, n2), count in co_occurence.items():
#     n1_x, n1_y = pos_x[n1], pos_y[n1]
#     n2_x, n2_y = pos_x[n2], pos_y[n2]

#     width = 2
#     if count > 5 and count <= 10:
#         width = 4
#     elif count > 10:
#         width = 6
#     p1.line([n1_x, n2_x], [n1_y, n2_y], line_color="#aeaeae", line_width=width)
# scatter = p1.circle('x', 'y', source=p1_source, color='color', size=26)
# p1_hover.renderers.append(scatter)


# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------
# # ---------------- TIME-SERIES GRAPH ------------------------------------
# # ------------------------------------------------------------------------
# # ------------------------------------------------------------------------
# tp1 = figure(title="Distribution of total hashtag count", **tp_params)
# # tp1.vbar(x='time', top='nTags', bottom=0, source=tp1_source, color="#CAB2D6")

# tp1.line('time', 'nTags', source=tp1_source, selection_color="orange", line_width=3)
# tp1.circle('time', 'nTags', size=8, source=tp1_source, fill_color="white", selection_color="orange")
# tp1.add_tools(tp1_hover)

# tp2 = figure(**tp_params)
# tp2.line('time', 'count', source=tp2_source, color='#007380', selection_color="orange", line_width=3)
# tp2.circle('time', 'count', size=8, source=tp2_source, fill_color="white", selection_color="orange")
# tp2.add_tools(tp2_hover)

# tp1_hover = HoverTool(
#     tooltips=[
#         ("Time period", "@time{%H:%M}"),
#         ("# of tweets", "@nTweets"),
#         ("# of hashtags", "@nTags")
#     ],
#     formatters={'time': 'datetime'},
#     mode='vline'
# )
# tp2_hover = HoverTool(
#     tooltips=[
#         ("Time period", "@time{%H:%M}"),
#         ("Count", '@count')
#     ],
#     formatters={'time': 'datetime'},
#     mode='vline'
# )


tweet_area = PreText(text='', width=1200, height=800)
sent_tweet_area = PreText(text='', width=1200, height=800)

# # Set up figure parameters
# p1.grid.visible = False
# p1.axis.visible = False
# p1.outline_line_color = None
# tp1.yaxis.axis_label = tp2.yaxis.axis_label = 'Count'
# tp1.title.text_font_size = tp2.title.text_font_size = p1.title.text_font_size = '14px'

# # Set up selection widgets
# time_ticker = Select(title='Period:', value='10Min', options=period)
# hashtag_ticker = Select(title='Hashtag:', value='#KronosStar', options=unique_hashtags)


# def update_tweet(attrname, old, new):
#     selected = tp2_source.selected['1d']['indices']
#     t1, t2 = time_ticker.value, hashtag_ticker.value

#     tweet_area.text = '      Date time      |                Tweet       \n'
#     tweet_area.text += '===============================================================================\n'
#     time_stamps, df_list = zip(*df.groupby(pd.TimeGrouper(freq=t1)))
#     for i in selected:
#         for time, r in df_list[i].iterrows():
#             if t2 in r['hashtags']:
#                 line = str(time) + '  |  ' + r['tweet'] + '\n'
#                 tweet_area.text += line


def update_sent_tweet(attrname, old, new):
    selected = sent_source.selected['1d']['indices'][0]

    text = 'Positive tweets \n'
    text += '===============================================================================\n'
    for pos_tw in sent_source.data['pos_tweets'][selected]:
        text += (pos_tw + '\n')

    text += '\n\nNegative tweets \n'
    text += '===============================================================================\n'
    for neg_tw in sent_source.data['neg_tweets'][selected]:
        text += (neg_tw + '\n')
    sent_tweet_area.text = text

# def update():
#     t1, t2 = time_ticker.value, hashtag_ticker.value
#     tp1_source.data, tp2_source.data = get_data(t1, t2)

#     tp1.xaxis.axis_label = tp2.xaxis.axis_label = "Time (" + t1 + ")"
#     tp2.title.text = "Distribution of Hashtag: {}".format(t2)


# time_ticker.on_change('value', lambda attr, old, new: update())
# hashtag_ticker.on_change('value', lambda attr, old, new: update())
# tp2_source.on_change('selected', update_tweet)
sent_source.on_change('selected', update_sent_tweet)

# # Set up layouts
# time_widget = column(row(time_ticker, hashtag_ticker), tp1, tp2)
# layout = column(row(time_widget, p1, p_cloud), tweet_area)

# # Initialize
# update()

curdoc().add_root(column(plot, sent_tweet_area))
curdoc().title = 'VAST Challenge, 2014 MC3'
