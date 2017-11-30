import codecs

Pos_path = "./data/opinion-lexicon-English/positive-words.txt"
Neg_path = "./data/opinion-lexicon-English/negative-words.txt"


def read2list(filepath):
    ret_list = set()
    with codecs.open(filepath, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s == "" or s.startswith(";"):
                continue
            ret_list.add(s)
    return ret_list


pos_list = read2list(Pos_path)
neg_list = read2list(Neg_path)


def posSent(sent):
    tokens = sent.split()
    for token in tokens:
        if token in pos_list:
            return True
    return False


def negSent(sent):
    tokens = sent.split()
    for token in tokens:
        if token in neg_list:
            return True
    return False


def sentScore(sent):
    score = 0
    for token in sent.split():
        if token in pos_list:
            score += 1
        elif token in neg_list:
            score -= 1
    return score


def getSentWords(sent):
    words = []
    for token in sent.split():
        if token in pos_list:
            words.append(token)
        elif token in neg_list:
            words.append(token)
    return words


if __name__ == "__main__":
    print(posSent("good movie"))
