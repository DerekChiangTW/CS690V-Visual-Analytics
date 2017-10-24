#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from utils import preprocess

# Read in dataset
fpath = './../data/VAST-2014-MC3/1700-1830.csv'
df = pd.read_csv(fpath, encoding='utf-8')

# Preprocess text data
tweets = preprocess(df['message'].tolist())
