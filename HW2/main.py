import pandas as pd
from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.palettes import Spectral6
from bokeh.models import (
    ColumnDataSource, CustomJS, Slider, Span,
    SingleIntervalTicker, NumeralTickFormatter,
    TapTool, HoverTool, BoxSelectTool, BoxZoomTool, LassoSelectTool
)
from bokeh.layouts import column, row, widgetbox
from bokeh.models.widgets import (
    CheckboxGroup, Select, Div, Panel, Tabs,
    DataTable, DateFormatter, TableColumn, NumberFormatter
)
from scipy.stats import pearsonr
from sklearn import linear_model
from bokeh.transform import dodge


# Default settings
COLOR_TICKERS = ["None", "Channel", "Region"]
DEFAULT_TOOLS = "pan,box_zoom,lasso_select,reset"
METHODS = ['Original', 'Mean', 'Median', 'Linear Regression']
COLORS = ['#0e824a', '#762ae0', '#6c7007', '#c30606']
COLORMAP={
    "Channel": {1:Spectral6[0], 2:Spectral6[1]},
    "Region": {1:Spectral6[0], 2:Spectral6[1] , 3:Spectral6[4]}}

def process_data():
    df = pd.read_csv(join(dirname(__file__), "data/Wholesale customers data-missing.csv"))
    clean_df = df.dropna()

    missing_list = list()
    for idx, row in df.iterrows():
        for i in range(len(row)):
            if pd.isnull(row[i]):
                missing_list.append((idx, row.index[i]))

    origin_df = pd.read_csv(join(dirname(__file__), "data/Wholesale customers data.csv"))
    result_df = pd.DataFrame()
    for idx, col in missing_list:
        r = pd.Series([origin_df[col].loc[idx], df.mean()[col], df.median()[col], 0], index=METHODS, name=str(idx))
        result_df = result_df.append(r)

    return df, clean_df, result_df, missing_list

def nix(val, lst):
    return [x for x in lst if x != val]

def find_missing(t1, t2):
    s = "<p>"
    for idx, row in df.loc[:, (t1, t2)].iterrows():
        for i in range(len(row)):
            if pd.isnull(row[i]):
                s += "Index {0}: {1}<br />".format(idx, row.index[i])
    s += "</p>"
    return s

def get_data(t1, t2, t3, checkbox_list):
    temp = df.loc[:, (t1, t2)]
    temp['size'] = 10
    temp['alpha'] = 0.5
    temp['index'] = list(df.index)

    if t3 == 'None':
        temp['color'] = Spectral6[0]
    else:
        temp['color'] = [COLORMAP[t3][x] for x in df[t3]]

    for idx, row in df.loc[:, (t1, t2)].iterrows():
        for i, val in row.iteritems():
            if pd.isnull(val):
                for num in checkbox_list:
                    row[i] = result_df[METHODS[num]].loc[str(idx)]
                    row['color'] = COLORS[num]
                    row['size'] = 14
                    row['alpha'] = 1.0
                    row['index'] = idx
                    temp = temp.append(row)
    return dict(x=temp[t1], y=temp[t2], index=temp['index'], size=temp['size'], color=temp['color'], alpha=temp['alpha'])

def predict_with_linear_regression(X_train, y_train, X_test):
    regr = linear_model.LinearRegression()
    regr.fit(X_train, y_train)
    return regr.predict(X_test)


# Read in dataset
df, clean_df, result_df, missing_list = process_data()
columns = sorted(df.columns[2:])

# Draw an interactive scatter plot to show the data distribution
s1 = ColumnDataSource(data=dict(x=[], y=[], index=[], size=[], color=[], alpha=[]))
scatter_plot = figure(plot_width=700, plot_height=500,tools=DEFAULT_TOOLS, toolbar_location='above')
scatter_plot.circle('x', 'y', source=s1, size='size', color='color', alpha='alpha')
scatter_plot.title.text_font_size='16px'
scatter_plot.xaxis.formatter=scatter_plot.yaxis.formatter=NumeralTickFormatter(format="$ 0,0")
hover = HoverTool(
        tooltips=[
            ("Index: ", "@index"),
            ("x: ", "@x{$ 0,0}"),
            ("y: ", "@y{$ 0,0}")
        ]
    )
scatter_plot.add_tools(hover)


# Set up tab1 widget
DEFAULT_TICKERS = columns
ticker1 = Select(title="X Axis:", value="Milk", options=nix("Fresh", DEFAULT_TICKERS))
ticker2 = Select(title="Y Axis:", value="Fresh", options=nix("Milk", DEFAULT_TICKERS))
ticker3 = Select(title="Color:", value="None", options=COLOR_TICKERS)
checkboxes = CheckboxGroup(labels=METHODS, active=[1,2])
info = Div(height=70)
tickers = widgetbox(ticker1, ticker2, ticker3)
info_widget = widgetbox(Div(text="<h2>Missing Values</h2>"), info)
checkbox_widget = widgetbox(Div(text="<h2>Fill With</h2>"), checkboxes)


# Set up callbacks
def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker3_change(attrname, old, new):
    update()

def checkbox_change(attrname, old, new):
    update()

def update():
    t1, t2, t3 = ticker1.value, ticker2.value, ticker3.value
    s1.data = get_data(t1, t2, t3, checkboxes.active)
    scatter_plot.xaxis.axis_label = t1 + " (m.u.)"
    scatter_plot.yaxis.axis_label = t2 + " (m.u.)"
    scatter_plot.title.text = "%s vs. %s" % (t1, t2)
    info.text = find_missing(t1, t2)

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)
ticker3.on_change('value', ticker3_change)
checkboxes.on_change('active', checkbox_change)


# Draw a table to show the pearson correlation matirx
pearson_df = clean_df[columns].corr(method='pearson')
pearson_df['Header'] = pearson_df.index
s2 = ColumnDataSource(pearson_df)
pcolumns = [TableColumn(field='Header', title='')]
pcolumns += [TableColumn(field=columns[x], title=columns[x], formatter=NumberFormatter(format="0.000")) for x in range(len(columns))]
data_table = DataTable(source=s2, columns=pcolumns, row_headers=False, fit_columns=True, width=700, height=180)
table1 = widgetbox(Div(text="<h2>Pearson correlation</h2>"), data_table)


# Draw a table to demonstrate the most related feature
max_index = list()
for col in pearson_df.columns[:-1]:
    max_index.append([pearson_df[col].drop(col).argmax()])
correlated = dict(zip(pearson_df.columns[:-1], max_index))
correlated['Header'] = ['Most correlated']
s3 = ColumnDataSource(data=correlated)
mcolumns = [TableColumn(field='Header', title='')]
mcolumns += [TableColumn(field=columns[x], title=columns[x]) for x in range(len(columns))]
feature_table = DataTable(source=s3, columns=mcolumns, row_headers=False, fit_columns=True, width=700, height=100)
table2 = widgetbox(
    Div(text="<h2>Most correlated</h2>"), 
    Div(text="<p>For each feature, find the most correlated feature based on pearson correlation.</p>", width=700),
    feature_table)
for idx, col in missing_list:
    X_train = clean_df[correlated[col][0]][:, None]
    y_train = clean_df[col][:, None]
    X_test = df[correlated[col][0]].loc[idx]
    linear_result = predict_with_linear_regression(X_train, y_train, X_test)
    result_df['Linear Regression'].loc[str(idx)] = linear_result


# Draw a vbar plot to compare the results
s4 = ColumnDataSource(data=dict(
    Index=result_df.index,
    Original=result_df['Original'],
    Mean= result_df['Mean'],
    Median= result_df['Median'],
    Linear_Regression= result_df['Linear Regression'])
)
bar_plot = figure(x_range=list(result_df.index), y_range=(0, 9000), plot_width=700, plot_height=280,
    toolbar_location='right', tools="pan,box_zoom,reset")
bar_plot.vbar(x=dodge('Index', -0.3, range=bar_plot.x_range), top='Original', width=0.15, source=s4,
    color="#c9d9d3", legend="original")
bar_plot.vbar(x=dodge('Index', -0.1, range=bar_plot.x_range), top='Mean', width=0.15, source=s4,
    color="#718dbf", legend="mean")
bar_plot.vbar(x=dodge('Index',  0.1,  range=bar_plot.x_range), top='Median', width=0.15, source=s4,
    color="#2171b5", legend="median")
bar_plot.vbar(x=dodge('Index',  0.3, range=bar_plot.x_range), top='Linear_Regression', width=0.15, source=s4,
    color="#e84d60", legend="linear regression")
bar_plot.xaxis.axis_label = 'Index'
bar_plot.x_range.range_padding = 0.05
bar_plot.xgrid.grid_line_color = None
bar_plot.legend.location = "top_right"
bar_plot.legend.orientation = "horizontal"
bar_plot.legend.click_policy="hide"


# Set up layout
desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=700, height=120)
scatter_widget = row(scatter_plot, column(tickers, info_widget, checkbox_widget))
tables = column(table1, table2)
bars = column(
    Div(text="<h2>Missing Values Comparison</h2>", height=20),
    Div(text="<p>For each missing data, compare the original value with different solutions.<br />\
        <b>Note: </b> For linear regression, I only use the most correlated feature (1 dimension) to predict.</p>", width=700, height=30),
    bar_plot)
bar_widget = column(tables, bars)
tab1 = Panel(child=scatter_widget, title="Scatter")
tab2 = Panel(child=bar_widget, title="Statistics")
tabs = Tabs(tabs=[tab1, tab2])
layout = column(desc, tabs)

# Initialize
update()

curdoc().add_root(layout)
curdoc().title = "Wholesale Customers"
