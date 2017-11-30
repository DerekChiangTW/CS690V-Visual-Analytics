#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pandas as pd
from itertools import combinations
from datetime import datetime
from nltk.tokenize import TweetTokenizer


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
    hashtag_re = re.compile(r"#\w+[\w'-]*\w+")
    hashtags = [token for token in tknzr.tokenize(tweet) if re.match(hashtag_re, token)]
    return hashtags


def count_cooccurence(tag_table, top_tags):
    """ Count the co-occurence of the hashtags.

    Parameters
    ----------
    tag_table : Series
        A Series of hashtags in each tweet.

    tag2id : dict
        A look-up dictionary to match the hashtag with indices.

    Returns
    -------
    co_occurence : dict
        A dictionary which counts the co-occurence of hashtags.

    """
    co_occurence = dict()
    tag2id = dict(zip(top_tags, range(len(top_tags))))
    for tag_list in tag_table:
        indices = [tag2id[t] for t in tag_list if t in top_tags]
        for pair in combinations(indices, 2):
            co_occurence[pair] = co_occurence.get(pair, 0) + 1
    return co_occurence
