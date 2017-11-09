from bokeh.io import output_notebook, show, curdoc
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.models.widgets import RadioGroup, Select, TextInput, Panel, Tabs, PreText
from bokeh.models import CustomJS, HoverTool, ResetTool, BoxZoomTool
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.plotting import figure
from sklearn.cluster import Birch, KMeans
from sklearn.manifold import TSNE
from scripts.utils import preprocess_a_tweet, str2time
from scripts.sentiment import posSent, negSent
from wordcloud import WordCloud
import numpy as np
import datetime
import pdb

# Read in dataset
fpath = './data/VAST-2014-MC3/1700-1830.csv'
ori_df = pd.read_csv(fpath)
tweet_df = ori_df["message"]
time_df = ori_df["date(yyyyMMddHHmmss)"]

# processed & group
tweet_se = tweet_df.apply(preprocess_a_tweet)
time_se = time_df.apply(str2time)
tweet_se.index = time_se
#grouped = tweet_se.groupby(tweet_se.index.map(lambda t: (t.hour, t.minute)))
grouped = tweet_se.groupby(tweet_se.index.map(lambda t: str(t.hour).zfill(2) + str(t.minute).zfill(2)))
tweets = tweet_se.tolist()
# cluster
vectorizer = CountVectorizer(max_features=50, stop_words="english")
countVector = vectorizer.fit_transform(tweets)
analyze = vectorizer.build_analyzer()

tweet_vecs = countVector.toarray()
vocab = vectorizer.get_feature_names()

# word cloud
def img2bokeh(input_image):
    xdim, ydim = input_image.size
    input_image = input_image.resize((xdim, ydim))
    input_image = input_image.convert("RGBA")
    img = np.empty((ydim , xdim), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
    view[:,:,:] = np.flipud(np.asarray(input_image))
    dim = max(xdim, ydim)
    return view, dim

wordcloud = WordCloud(background_color="white").generate(" ".join(tweets))
p_image, dim = img2bokeh(wordcloud.to_image())
p_cloud = figure(x_range=(0, dim), y_range=(0, dim), plot_width=400, plot_height=300, title="Real-time wordcloud")
p_cloud.xaxis.visible = False
p_cloud.yaxis.visible = False
p_cloud.image_rgba(image=[p_image], x=0, y=0, dw=dim, dh=dim)

# kmeans
k_cluster = 4
km = KMeans(n_clusters=k_cluster, random_state=0)
km.fit(tweet_vecs)
predictions_km = km.predict(tweet_vecs)

# tsne
model = TSNE(n_components=2, random_state=0)
tsne_vecs = model.fit_transform(tweet_vecs)

# visualize
ALL_COLORS = ['red', 'blue', "green", "orange", "yellow", "purple", "black", "brown", 'cyan' "gold", "grey"]
def get_colors(labels):
    colors=[]
    for i in labels:
        if i > 11:
            print("Require more color")
        colors.append(ALL_COLORS[int(i)])
    return colors
colors_km = get_colors(predictions_km)


month_select_1 = Select(value='17', title="start hour", width=200, options = ["17", "18"] )
day_select_1 = Select(value="0", title="start minute", width=200, options = [str(i) for i in range(1, 60)] )
month_select_2 = Select(value="18", title="end hour", width=200, options = ["17","18"] )
day_select_2 = Select(value="34", title="end minute", width=200, options = [str(i) for i in range(1, 60)] )

hover1 = HoverTool(tooltips=[('Tweet', '@tweet')])

km_data = ColumnDataSource(data=dict(colors=colors_km, x=tsne_vecs[:,0], y=tsne_vecs[:,1], tweet=tweets))
km_plot=figure(plot_width=400, plot_height=400, toolbar_location='right', title='KMeans', tools=[hover1, BoxZoomTool(), ResetTool()])
km_plot.circle('x','y', line_color='colors', fill_color='colors', source=km_data)
s_slider = Slider(title="Num of cluster for KMeans", value=4.0, start=2.0, end=10.0, step=1, width=250)

def update_time_series(m1, d1, m2, d2):
    date_1 = datetime.datetime.strptime("20141231{0}{1}00".format(str(m1).zfill(2), str(d1).zfill(2)),'%Y%m%d%H%M%S')
    date_2 = datetime.datetime.strptime("20141231{0}{1}59".format(str(m2).zfill(2), str(d2).zfill(2)),'%Y%m%d%H%M%S')
    if  date_1 > date_2: #swith
        date_1, date_2 = date_2, date_1
    triggered = []
    time_stamps = []
    for hm, texts in grouped:
        date_ = datetime.datetime.strptime("20141231{0}00".format(hm),'%Y%m%d%H%M%S')
        if date_ >= date_1 and date_ <= date_2:
            triggered += texts.tolist()
            time_stamps += texts.index

    # update text area
    tweets = triggered
    update_sentiment(time_stamps, triggered)

    countVector = vectorizer.fit_transform(triggered)
    tweet_vecs = countVector.toarray()

    k_cluster = int(s_slider.value)
    km = KMeans(n_clusters=k_cluster, random_state=0)
    km.fit(tweet_vecs)
    predictions_km = km.predict(tweet_vecs)
    colors_km = get_colors(predictions_km)

    tsne_vecs = model.fit_transform(tweet_vecs)
    km_data.data = dict(colors=colors_km, x=tsne_vecs[:,0], y=tsne_vecs[:,1], tweet=triggered)

    # update wordcloud
    wordcloud = WordCloud(background_color="white").generate(" ".join(tweets))
    p_image, dim = img2bokeh(wordcloud.to_image())
    p_cloud.image_rgba(image=[p_image], x=0, y=0, dw=dim, dh=dim)

    print("updated")

def update_s_clusters(attrname, old, new):
    k_cluster = int(s_slider.value)
    km = KMeans(n_clusters=k_cluster, random_state=0)
    km.fit(tweet_vecs)
    predictions = km.predict(tweet_vecs)
    colors = get_colors(predictions)
    km_data.data = dict(colors=colors, x=tsne_vecs[:,0], y=tsne_vecs[:,1], tweet=tweets)
s_slider.on_change('value', update_s_clusters)

def update_time_window(attrname, old, new):
    start_m = int(month_select_1.value)
    start_d = int(day_select_1.value)
    end_m = int(month_select_2.value)
    end_d = int(day_select_2.value)
    print(start_m, start_d, end_m, end_d)
    update_time_series(start_m, start_d, end_m, end_d)

month_select_1.on_change('value', update_time_window)
day_select_1.on_change('value', update_time_window)
month_select_2.on_change('value', update_time_window)
day_select_2.on_change('value', update_time_window)


def update_sentiment(time_stamps, tweets):
    cached = '      Date time                ||        Negative  Tweets       \n'
    cached += '===============================================================================\n'
    for time_, tweet_ in zip(time_stamps, tweets):
        if negSent(tweet_):
            cached += '      {0}      ||        {1}       \n'.format(str(time_), tweet_)

    cached += "\n\n\n"

    cached += '      Date time                ||        Positive  Tweets       \n'
    cached += '===============================================================================\n'
    for time_, tweet_ in zip(time_stamps, tweets):
        if posSent(tweet_):
            cached += '      {0}      ||        {1}       \n'.format(str(time_), tweet_)
    sent_tweets.text = cached

# sentiment
sent_tweets = PreText(text='', width=1000, height=800)
all_time = []
all_tweet = []
for hm, texts in grouped:
    all_tweet += texts.tolist()
    all_time += texts.index
update_sentiment(all_time, all_tweet)


inputs = widgetbox(s_slider)
l = layout([row(column(row(column(month_select_1, day_select_1), column(month_select_2, day_select_2)), 
    row(s_slider), row(km_plot), row(column(p_cloud))), column(sent_tweets))])
curdoc().add_root(l, inputs)
curdoc().title = "Clustering twitter with sliding window"


