#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from bokeh.io import curdoc
from os.path import dirname, join
from bokeh.plotting import figure
from bokeh.models import Label, Spacer, ColumnDataSource
from bokeh.layouts import column, row
from bokeh.models.widgets import Div, Select, CheckboxGroup

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from data import process_data


# Default settings
TARGETS = ['cancer', 'diabetes', 'heart_disease']
CLASSIFIERS = ['kNN', 'SVM', 'Decision Tree', 'Logistic Regression']
plot_params = {'plot_height': 400, 'plot_width': 550, 'responsive': True,
               'toolbar_location': 'above', 'tools': ''}
sidebar_width = 200


def get_classifier(alg):
    """ Set the classifier and parameters.

    Parameters
    ----------
        alg : string
            User-specified classification algorithm.

    Returns
    -------
        clf : estimator object
            Scikit-learn's estiamtor object.

    """

    if alg == 'kNN':
        clf = KNeighborsClassifier(n_neighbors=3)
    elif alg == 'SVM':
        clf = SVC(kernel='linear')
    elif alg == 'Decision Tree':
        clf = DecisionTreeClassifier(max_depth=5)
    elif alg == 'Logistic Regression':
        clf = LogisticRegression()

    return clf


# Read in dataset
df, feature_dict = process_data()
feature_names = list(feature_dict.keys())
feature_boxes = CheckboxGroup(labels=feature_names, active=[0, 1, 2, 3, 4])
s = ColumnDataSource(data=dict(x=[], real_y=[], predict_y=[]))

pred_ticker = Select(title='Predict:', value='cancer',
                     options=TARGETS, width=sidebar_width)
alg_ticker = Select(title='Classifier:', value='kNN',
                    options=CLASSIFIERS, width=sidebar_width)


# Plot the classification result
p = figure(**plot_params)
p.circle('x', 'real_y', source=s, size=16, alpha=1.0, legend='Actual')
p.circle('x', 'predict_y', source=s, size=24, alpha=0.4, legend='Predict')
p.xaxis.axis_label = 'test data'
p.yaxis.axis_label = 'label'
p.yaxis.ticker = [0, 1]
p.title.text_font_size = '16px'
p.legend.location = "center_left"
p.legend.click_policy = "hide"
p.min_border_right = 15

label = Label(x=4.2, y=0.45, text=str(), text_font_size='20pt', text_color='#b4b4b4')
p.add_layout(label)


# Set up callbacks
def setting_change(attr, old, new):
    update()


def update():
    pred, alg = pred_ticker.value, alg_ticker.value
    used_features = [feature_names[x] for x in feature_boxes.active]

    # Get the corresponding data based on user's selection
    feature_cols = []
    for f in used_features:
        feature_cols += feature_dict[f]
    X, y = df[feature_cols], df[pred]

    # Split the data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=0)
    clf = get_classifier(alg)
    clf.fit(X_train, y_train)
    y_hat_test = clf.predict(X_test)

    # Update the result plot
    xvals = list(range(1, len(X_test) + 1))
    s.data = dict(x=xvals, real_y=y_test, predict_y=y_hat_test)
    p.xaxis.ticker = xvals
    p.title.text = 'Predict {0} using {1}'.format(pred, alg)
    label.text = 'Accuracy: {0:.3f}'.format(clf.score(X_test, y_test))


pred_ticker.on_change('value', setting_change)
alg_ticker.on_change('value', setting_change)
feature_boxes.on_change('active', setting_change)


# Set up layout
fpath = join(dirname(__file__), 'description.html')
desc = Div(text=open(fpath).read(), width=700, height=140)

spacer = Spacer(width=sidebar_width, height=15)
text = Div(text="<h2>Features</h2>", height=10, width=sidebar_width)
feature_widget = column(text, feature_boxes)
sidebar = column(pred_ticker, alg_ticker, spacer, feature_widget)

layout = column(desc, row(p, sidebar))


# Initalize
update()

curdoc().add_root(layout)
curdoc().title = 'Food frequency questionaire survey'
