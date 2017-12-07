#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import operator
import networkx as nx
from itertools import combinations
from datetime import datetime
from nltk.tokenize import TweetTokenizer

hashtag_re = re.compile(r"#\w+[\w'-]*\w+")


def checkNaN(data):
    """ Check if the data contains NaN values. """
    if data.isnull().values.any():
        N = data.isnull().sum().sum()
        print("There are {} missing values.".format(N))


def preprocess(tweets):
    for i, t in enumerate(tweets):
        tweets[i] = preprocess_a_tweet(t)
    return tweets


def preprocess_a_tweet(t):
    ret_str = None
    t = t.lower()
    if t.startswith("rt @"):
        t = t[4:]
        pos = t.find(":")
        ret_str = t[: pos] + t[pos + 1:]
    else:
        ret_str = t
    ret_str = re.sub(r'[?|$|.|!|#|\-|"|\n|,|@|(|)]', r' ', ret_str)
    ret_str = re.sub(r'https?:\/\/.*[\r\n]*', '', ret_str, flags=re.MULTILINE)
    # ret_str = re.sub(r'[0|1|2|3|4|5|6|7|8|9|:]', r'$NUM$', ret_str)
    return ret_str


def str2time(s):
    """
    input could be integer
    """
    return datetime.strptime(str(s), '%Y%m%d%H%M%S')


def extract_hashtags(tweet):
    """ Extract hashtags from tweet.

    Parameters
    ----------
    tweet : string
        Raw tweet text.

    Returns
    -------
    hashtags : list of strings
        Tokenized strings starting with '#'.

    """
    tknzr = TweetTokenizer()
    hashtags = [token.lower() for token in tknzr.tokenize(tweet) if re.match(hashtag_re, token)]
    return hashtags


def run_pagerank(tag_table, unique_tags, targetNum):
    """ Run pagerank and return the top hashtags. """
    id2tag = {i: tag for i, tag in enumerate(unique_tags)}
    tag2id = {tag: i for i, tag in id2tag.items()}

    co_occurence = dict()
    for tag_list in tag_table:
        indices = [tag2id[tag] for tag in tag_list]
        for pair in combinations(indices, 2):
            co_occurence[pair] = co_occurence.get(pair, 0) + 1

    nodes = range(len(unique_tags))
    edges = [(pair[0], pair[1], weight) for pair, weight in co_occurence.items()]
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    pr = nx.pagerank(G, weight='weight')

    top_indices, top_scores = zip(*sorted(pr.items(), key=operator.itemgetter(1), reverse=True)[:targetNum])
    topTags = [id2tag[i] for i in top_indices]
    return topTags
