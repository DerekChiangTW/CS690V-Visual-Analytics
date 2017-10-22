from bokeh.io import output_notebook, show, curdoc
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.models.widgets import RadioGroup, Select, TextInput, Panel, Tabs
from bokeh.models import CustomJS
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.plotting import figure
from sklearn.cluster import Birch, KMeans
from sklearn.manifold import TSNE
import pdb

# Read in USA Geolocated Twitter dataset
fpath = './data/USA-Geolocated-tweets/dashboard_x_usa_x_filter_nativeretweets.xlsx'
df = pd.read_excel(fpath, sheetname='Stream')
tweets = df['Tweet content']
tweets = tweets.tolist()
#pdb.set_trace()

def preprocess(tweets):
    for i, t in enumerate(tweets):
        t = t.lower()
        if t.startswith("rt @"):
            t = t[4:]
            pos= t.find(":")
            tweets[i] = t[ : pos] + t[pos + 1:]
        else:
            tweets[i] = t

    for i, t in enumerate(tweets):
        tweets[i] = re.sub(r'[?|$|.|!|#|\-|"|\n|,|@|(|)]',r'',tweets[i])
        tweets[i] = re.sub(r'https?:\/\/.*[\r\n]*', '', tweets[i], flags=re.MULTILINE)
        tweets[i] = re.sub(r'[0|1|2|3|4|5|6|7|8|9|:]',r'$NUM$',tweets[i]) 
    return tweets

# print(preprocess(['rt @spurs: hello']))
tweets = preprocess(tweets)
tweets = tweets[ : 1000]

# cluster
vectorizer = CountVectorizer(max_features=50, stop_words="english")
countVector = vectorizer.fit_transform(tweets)
analyze = vectorizer.build_analyzer()

tweet_vecs = countVector.toarray()
vocab = vectorizer.get_feature_names()

# kmeans
k_cluster = 7
km = KMeans(n_clusters=k_cluster, random_state=0)
km.fit(tweet_vecs)
predictions_km = km.predict(tweet_vecs)

# birch
n_clusters=7
brc = Birch(branching_factor=500, n_clusters=n_clusters, threshold=0.5,  compute_labels=True)
brc.fit(tweet_vecs)
predictions =brc.predict(tweet_vecs)
#pdb.set_trace()

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
colors = get_colors(predictions)

km_data = ColumnDataSource(data=dict(colors=colors_km, x=tsne_vecs[:,0], y=tsne_vecs[:,1]))
km_plot=figure(plot_width=300, plot_height=300, toolbar_location='right', title='KMeans')
km_plot.circle('x','y', line_color='colors', fill_color='colors', source=km_data)
s_slider = Slider(title="Num of cluster for KMeans", value=7.0, start=2.0, end=10.0, step=1, width=250)

brc_data = ColumnDataSource(data=dict(colors=colors, x=tsne_vecs[:,0], y=tsne_vecs[:,1]))
brc_plot=figure(plot_width=300, plot_height=300, toolbar_location='right', title='Birch')
brc_plot.circle('x','y', line_color='colors', fill_color='colors', source=brc_data)
k_slider = Slider(title="Num of cluster for Birch", value=7.0, start=2.0, end=10.0, step=1, width=250)


def update_k_clusters(attrname, old, new):
    k_cluster = int(k_slider.value)
    brc = Birch(branching_factor=50, n_clusters=k_cluster, threshold=0.5,  compute_labels=True)
    brc.fit(tweet_vecs)
    predictions = brc.predict(tweet_vecs)
    colors = get_colors(predictions)
    brc_data.data = dict(colors=colors, x=tsne_vecs[:,0], y=tsne_vecs[:,1])
k_slider.on_change('value', update_k_clusters)

def update_s_clusters(attrname, old, new):
    k_cluster = int(k_slider.value)
    km = KMeans(n_clusters=k_cluster, random_state=0)
    km.fit(tweet_vecs)
    predictions = km.predict(tweet_vecs)
    colors = get_colors(predictions)
    km_data.data = dict(colors=colors, x=tsne_vecs[:,0], y=tsne_vecs[:,1])
s_slider.on_change('value', update_s_clusters)


inputs = widgetbox(k_slider)
l = layout([row(column(brc_plot, k_slider), column(km_plot, s_slider))])
curdoc().add_root(l, inputs)
curdoc().title = "Clustering twitter"

