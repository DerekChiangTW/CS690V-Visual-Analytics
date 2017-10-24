#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from itertools import combinations


def preprocess(tweets):
    for i, t in enumerate(tweets):
        t = t.lower()
        if t.startswith("rt @"):
            t = t[4:]
            pos = t.find(":")
            tweets[i] = t[: pos] + t[pos + 1:]
        else:
            tweets[i] = t

    for i, t in enumerate(tweets):
        tweets[i] = re.sub(r'[?|$|.|!|#|\-|"|\n|,|@|(|)]', r'', tweets[i])
        tweets[i] = re.sub(r'https?:\/\/.*[\r\n]*', '', tweets[i], flags=re.MULTILINE)
        tweets[i] = re.sub(r'[0|1|2|3|4|5|6|7|8|9|:]', r'$NUM$', tweets[i])
    return tweets


def extract_hashtags(tweets, threshold):
    """ Extract hashtags from tweets and index them.

    Parameters
    ----------
        tweets : list of strings
            Raw tweet text.

        threshold : int
            Set the threshold for the count of hashtag. A hashtag
            is extracted if its count is higher than the threshold.

    Returns
    -------
        id2word : dict
            Index the extracted hashtags.

        word2id : dict
            Provide a look-up dictionary.

    """
    hashtag_count = dict()
    for tweet in tweets:
        for tag in re.findall('#([\w\d]+)', tweet.lower()):
            hashtag_count[tag] = hashtag_count.get(tag, 0) + 1

    # Extract hashtags with count higher than threshold
    top_hashtags = set(tag for tag, count in hashtag_count.items() if count > threshold)

    id2word = {i: tag for i, tag in enumerate(sorted(top_hashtags))}
    word2id = {tag: i for i, tag in id2word.items()}

    return id2word, word2id


def count_cooccurence(tweets, word2id):
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
    for tweet in tweets:
        matches = re.findall('#([\w\d]+)', tweet.lower())
        indices = sorted([word2id[word] for word in matches if word in word2id.keys()])
        for pair in combinations(indices, 2):
            co_occurence[pair] = co_occurence.get(pair, 0) + 1

    return co_occurence
