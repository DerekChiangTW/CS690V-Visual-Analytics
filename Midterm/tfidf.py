from bokeh.io import output_notebook, show, curdoc
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer, TfidfTransformer
import matplotlib.pyplot as plt
import numpy as np
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

def tfidf(text):
    vectorizer = TfidfVectorizer()
    transformer = TfidfTransformer()
    countVector = vectorizer.fit_transform(text)
    mat = transformer.fit_transform(countVector.toarray()).toarray()
    analyze = vectorizer.build_analyzer()

    threshold = 0.0001
    key_dict = {}
    for i in range(len(text)):
        tokens = analyze(text[i])
        for j in range(len(tokens)):
            if mat[i][j] > threshold:
                key_dict[tokens[j]] = mat[i][j]
    l1, l2 = [],[]
    s = [ (k, key_dict[k]) for k in sorted(key_dict, key=key_dict.get)]
    for k, v in s:
        l1.append(k)
        l2.append(v)
    return l1, l2


# rank using tf idf
words, scores = tfidf(tweets)
#pdb.set_trace()

def plot(words, scores):
    fig = plt.figure(figsize=(12, 9), facecolor="w")
    x = np.arange(len(words))
    ax = fig.add_subplot(1, len(words), 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_frame_on(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_xlabel("Tf-Idf Score", labelpad=16, fontsize=14)
    ax.ticklabel_format(axis='x', style='sci', scilimits=(-2,2))
    ax.barh(x, scores, align='center', color='#3F5D7D')
    ax.set_yticks(x)
    ax.set_ylim([0, x[-1]+0.005])
    yticks = ax.set_yticklabels(words)
    plt.subplots_adjust(bottom=0.09, right=0.97, left=0.15, top=0.95, wspace=0.52)
    plt.show()

plot(words, scores)