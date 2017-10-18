import re
import pandas as pd
from itertools import combinations


def extract_hashtags(tweets):
    """ Extract the hashtags from the tweets and index them. """

    hashtags = set()
    for text in tweets:
        hashtags.update(re.findall('#([\w\d]+)', text.lower()))
    word2id = {tag: i for i, tag in enumerate(sorted(hashtags))}
    id2word = {i: tag for tag, i in word2id.items()}
    
    return word2id, id2word

def count_cooccurence(tweets, word2id):
    """ Count the co-occurence of the hashtags. """
    
    co_occurence = dict()
    for tweet in tweets:
        matches = re.findall('#([\w\d]+)', tweet.lower())
        indices = sorted([word2id[hashtag] for hashtag in matches])
        for pair in combinations(indices, 2):
            co_occurence[pair] = co_occurence.get(pair, 0) + 1

    return co_occurence