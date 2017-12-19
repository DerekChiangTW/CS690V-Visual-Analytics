from collections import namedtuple, defaultdict
import os
import spacy
import codecs
import pdb

nlp = spacy.load('en', disable=['parser'])
Article = namedtuple('Article', ['strid', 'title', 'time', 'sentences'])

# the key is token, value is (articlue object and list of sentence index)
inveted_index = dict()

article_dir = "./data/MC1/MC1_Data/MC1_Data/articles"

id2ent = []
ent2id = {}
id2sent = []
sent2id = {}
ent2sent = defaultdict(list) 
sent2ent = defaultdict(list)
def read_data():
    for filename in os.listdir(article_dir):
        if "txt" not in filename:
            continue
        with codecs.open(os.path.join(article_dir, filename), encoding='utf-8') as f:
            try:
                lines = f.readlines()
            except:
                continue

            for line in lines:
                
                # dumplicate sents
                if line in id2sent:
                    continue

                line = line.strip()

                doc = nlp(line)
                # pdb.set_trace()

                local_ent_list = []
                for ent in doc.ents:
                    if ent.label_ in ['ORG', 'PERSON']:
                        if '-' in ent.text or len(ent.text) > 30:
                            continue
                        local_ent_list.append(ent.text)
                        if ent.text not in id2ent:
                            id2ent.append(ent.text)
                            ent2id[ent.text] = len(id2ent)
                
                id2sent.append(line)
                sent2id[line] = len(id2sent)
                sent2ent[sent2id[line]] = local_ent_list
                for ent_str in local_ent_list:
                    if ent_str in line:
                        ent2sent[ent2id[ent_str]].append(sent2id[line])

read_data()

print("Loading successfully!")
#print(id2ent)
# print(ent2sent)