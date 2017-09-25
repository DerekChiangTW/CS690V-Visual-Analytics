import pandas as pd
from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Slider, NumeralTickFormatter,
    TapTool, HoverTool, BoxSelectTool, BoxZoomTool, LassoSelectTool
)
from bokeh.layouts import column, row, widgetbox
from bokeh.models.widgets import (
    CheckboxGroup, Select, Div, Panel, Tabs,
    DataTable, TableColumn, NumberFormatter
)
from sklearn.cluster import KMeans, SpectralClustering


def nix(val, lst):
    return [x for x in lst if x != val]

def get_data(t1, t2, t3, clusters):
    
    if t3 == METHODS[0]:
        # Run K-means clustering
        labels, centroids = run_Kmeans(data, clusters)

        # For K-means clustering, plot the centroid of each cluster
        index=["Cluster "+str(i+1) for i in range(clusters)]
        x = [coord[columns.index(t1)] for coord in centroids]
        y = [coord[columns.index(t2)] for coord in centroids]
        source2.data = dict(index=index, x=x, y=y, color=COLORS[:clusters])
        plot.circle_x('x', 'y', source=source2, size=20, color='color', fill_alpha=1.0, line_color='black', line_width=2)
    
    elif t3 == METHODS[1]:
        # Run Spectral clustering
        labels = run_SpectralClustering(data, clusters)

    temp = df.loc[:, (t1, t2)]
    temp['index'] = list(df.index)
    temp['color'] = [COLORS[x] for x in labels]

    return dict(index=temp['index'], x=temp[t1], y=temp[t2], color=temp['color'])

def run_Kmeans(data, clusters):
    estimator = KMeans(n_clusters=clusters, random_state=0).fit(data)
    return estimator.labels_, estimator.cluster_centers_

def run_SpectralClustering(data, clusters):
    estimator = SpectralClustering(n_clusters=clusters, random_state=0).fit(data)
    return estimator.labels_


# Read in dataset
df = pd.read_csv(join(dirname(__file__), "data/Wholesale customers data.csv"))
columns = sorted(df.columns[2:])
data = df[columns].as_matrix()
source1 = ColumnDataSource(data=dict(index=[], x=[], y=[], color=[]))
source2 = ColumnDataSource(data=dict(index=[], x=[], y=[], color=[]))


# Default settings
DEFAULT_TICKERS = columns
DEFAULT_TOOLS = "pan,box_zoom,lasso_select,reset"
METHODS = ['K-means', 'Spectral']
COLORS = ['#ae254a', '#007380', '#4364ae', '#f9d500',
          '#ff7256', '#800080', '#0e2f44', '#f442cb']


# Draw an interactive scatter plot to show the data distribution
plot = figure(plot_width=700, plot_height=500, responsive=True, tools=DEFAULT_TOOLS, toolbar_location='above')
plot.circle('x', 'y', source=source1, size=12, color='color', alpha=0.5)
plot.title.text_font_size='16px'
plot.xaxis.formatter=plot.yaxis.formatter=NumeralTickFormatter(format="$ 0,0")

# Add a hover tool to the scatter plot
hover = HoverTool(
        tooltips=[
            ("Index: ", "@index"),
            ("x: ", "@x{$ 0,0}"),
            ("y: ", "@y{$ 0,0}")
        ]
    )
plot.add_tools(hover)


# Set up widget
ticker1 = Select(title="X Axis:", value="Milk", options=nix("Fresh", DEFAULT_TICKERS))
ticker2 = Select(title="Y Axis:", value="Fresh", options=nix("Milk", DEFAULT_TICKERS))
ticker3 = Select(title="Clustering:", value="K-means", options=METHODS)
tickers = widgetbox(ticker1, ticker2, ticker3)
cluster_slider = Slider(title="Clusters", value=4, start=1, end=8, step=1)


# Set up callbacks
def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker3_change(attrname, old, new):
    update()

def slider_change(attrname, old, new):
    update()

def update():
    t1, t2, t3 = ticker1.value, ticker2.value, ticker3.value
    clusters = cluster_slider.value

    source1.data = get_data(t1, t2, t3, clusters)
    plot.xaxis.axis_label = t1 + " (m.u.)"
    plot.yaxis.axis_label = t2 + " (m.u.)"
    plot.title.text = "%s vs. %s" % (t1, t2)

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)
ticker3.on_change('value', ticker3_change)
cluster_slider.on_change('value', slider_change)


# Set up layout
desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=700, height=120)
scatter_widget = row(plot, column(tickers, cluster_slider))
layout = column(desc, scatter_widget)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = "Wholesale Customers"
