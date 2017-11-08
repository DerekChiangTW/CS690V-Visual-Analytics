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
    return datetime.strptime(str(s),'%Y%m%d%H%M%S')


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


def vectorize_hashtags(hashtags, tag2id):
    """ Vectorize hashtags based on co-occurence. """

    for tag_list in hashtags:
        indices = set([tag2id[tag] for tag in tag_list])
        print(indices)
        for pair in combinations(indices, 2):
            print(pair)
            # def count_hashtags(hashtags, threshold=0):
    """ Count hashtags and index them (Bag-of-Words).

    Parameters
    ----------
    hashtags : list of strings
        Tokenized strings starting with '#'.

    threshold : int
        The minimum count of occurence.

    Returns
    -------
    tag_count : dict

    """

    # tag_count = dict()

    # # Check if the input is a list/Series of strings
    # if isinstance(tweets, (list, pd.Series)):
    #     for tweet in tweets:
    #         for tag in re.findall(hashtag_re, tweet.lower()):
    #             tag_count[tag] = tag_count.get(tag, 0) + 1
    # else:
    #     for tag in re.findall(hashtag_re, tweets.lower()):
    #         tag_count[tag] = tag_count.get(tag, 0) + 1

    # # Extract hashtags with count higher than threshold
    # top_tags = {t: c for t, c in tag_count.items() if c > threshold}
    # return top_tags


def count_cooccurence(tag_table, word2id):
    """ Count the co-occurence of the hashtags.

    Parameters
    ----------
        tweets : list of strings
            Raw tweet text.

        word2id : dict
            A look-up dictionary to match the hashtag with indices.

    Returns
    -------
        co_occurence : dict
            A dictionary which counts the co-occurence of hashtags.
            The keys are tuples of hashtag indices and values are the count.

    """
    co_occurence = dict()
    for tag_dict in tag_table:
        indices = sorted([word2id[w] for w in tag_dict.keys() if w in word2id])
        for pair in combinations(indices, 2):
            co_occurence[pair] = co_occurence.get(pair, 0) + 1

    return co_occurence
