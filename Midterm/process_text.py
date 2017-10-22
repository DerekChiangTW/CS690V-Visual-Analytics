#Transfer pandas.core.series.Series to string
tweets=" ".join(tweets)

# preprocess text
def process_text(tweets):
#Remove emoji
    import re
    emoji=re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    tweets=emoji.sub(r'',tweets) 
#Convert to lower case
    tweets=tweets.lower()
#Remove www.* or https?://* 
    tweets = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweets)
#Remove @username 
    tweets = re.sub('@[^\s]+','USER',tweets)
#Remove punctuation
    tweets= re.sub(r'[?|$|.|!|#|\-|"|\n|,|@|(|)]',r'', tweets)
#Remove number
    tweets=re.sub(r'[0|1|2|3|4|5|6|7|8|9|:]',r'',tweets)
#trim
    tweets = tweets.strip('\'"')
#Tokenize text
    from nltk.tokenize import word_tokenize
    tweets = word_tokenize(tweets)
    return tweets 

tokens=process_text(tweets)