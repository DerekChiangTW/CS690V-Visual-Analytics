from bokeh.io import output_notebook, show, curdoc
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.models.widgets import RadioGroup, Select, TextInput, Panel, Tabs
from bokeh.models import CustomJS, HoverTool, ResetTool, BoxZoomTool
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.plotting import figure
from sklearn.cluster import Birch, KMeans
from sklearn.manifold import TSNE
from scripts.utils import preprocess_a_tweet
import datetime
import pdb

# Read in dataset
fpath = './data/costco/export_dashboard_cost_2016_06_15_12_24_55.xlsx'
df = pd.read_excel(fpath, sheetname='Stream')
tweet_df = df["Tweet content"][:1000]

# processed & group
tweet_se = tweet_df.apply(preprocess_a_tweet)
tweet_se.index = pd.to_datetime(df['Date'][:1000] + ' ' + df['Hour'][:1000])
tweets = tweet_se.tolist()
grouped = tweet_se.groupby(tweet_se.index.map(lambda t: (t.month, t.day)))
# pdb.set_trace()

# cluster
vectorizer = CountVectorizer(max_features=50, stop_words="english")
countVector = vectorizer.fit_transform(tweets)
analyze = vectorizer.build_analyzer()

tweet_vecs = countVector.toarray()
vocab = vectorizer.get_feature_names()

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


month_select_1 = Select(value='6', title="start month", width=200, options = ["5", "6"] )
day_select_1 = Select(value="1", title="start day", width=200, options = [str(i) for i in range(1, 30)] )
month_select_2 = Select(value="6", title="end month", width=200, options = ["5", "6"] )
day_select_2 = Select(value="10", title="end day", width=200, options = [str(i) for i in range(1, 30)] )

hover1 = HoverTool(tooltips=[('Tweet', '@tweet')])

km_data = ColumnDataSource(data=dict(colors=colors_km, x=tsne_vecs[:,0], y=tsne_vecs[:,1], tweet=tweets))
km_plot=figure(plot_width=300, plot_height=300, toolbar_location='right', title='KMeans', tools=[hover1, BoxZoomTool(), ResetTool()])
km_plot.circle('x','y', line_color='colors', fill_color='colors', source=km_data)
s_slider = Slider(title="Num of cluster for KMeans", value=4.0, start=2.0, end=10.0, step=1, width=250)

def update_time_series(m1, d1, m2, d2):
    date_1 = datetime.date(2016, m1, d1)  
    date_2 = datetime.date(2016, m2, d2)  
    if  date_1 > date_2: #swith
        date_1, date_2 = date_2, date_1
    triggered = []
    for (m_, d_), texts in grouped:
        date_ = datetime.date(2016, m_, d_)
        if date_ >= date_1 and date_ <= date_2:
            triggered += texts.tolist()

    countVector = vectorizer.fit_transform(triggered)
    tweet_vecs = countVector.toarray()

    k_cluster = int(s_slider.value)
    km = KMeans(n_clusters=k_cluster, random_state=0)
    km.fit(tweet_vecs)
    predictions_km = km.predict(tweet_vecs)
    colors_km = get_colors(predictions_km)

    tsne_vecs = model.fit_transform(tweet_vecs)
    km_data.data = dict(colors=colors_km, x=tsne_vecs[:,0], y=tsne_vecs[:,1], tweet=triggered)
    print("updated")

def update_s_clusters(attrname, old, new):
    k_cluster = int(s_slider.value)
    km = KMeans(n_clusters=k_cluster, random_state=0)
    km.fit(tweet_vecs)
    predictions = km.predict(tweet_vecs)
    colors = get_colors(predictions)
    km_data.data = dict(colors=colors, x=tsne_vecs[:,0], y=tsne_vecs[:,1])
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


inputs = widgetbox(s_slider)
l = layout([row(column(month_select_1, day_select_1), column(month_select_2, day_select_2)),
    row(column(km_plot, s_slider))])
curdoc().add_root(l, inputs)
curdoc().title = "Clustering twitter with sliding window"


