from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select, PreText, Button, Paragraph, Div
from bokeh.plotting import figure
from bokeh.layouts import widgetbox, row, column, layout
from reader import *
import pdb


text = TextInput(title="Keyword", value='leader')
# ner_select = Select(title="Candidate Entity", value="Henk Bodrogi", options=id2ent + ["None"])
ner_select = Select(title="Candidate Entity", value="None", options=id2ent + ["None"])
# cand_text = PreText(text='Search Result: \n', width=1000, height=800)
cand_text = Div(text='<p>Search Result: <\p>', width=1000, height=800)
search_icon = Button(label="search", button_type="success", width=100)

def update_ner(attrname, old, new):
    '''
    update the candidate sentences
    '''
    keyword = text.value
    entity = ner_select.value
    if entity == "None":
        entity = None
    html_str = search(keyword, entity=entity)
    cand_text.text = html_str
    search_icon.button_type="success"

def search(keyword, entity=None):
    '''
    return raw str highlighted html
    '''
    # pdb.set_trace()
    keywork = keyword.lower()
    ret_str = "<p>Search Result: </p>"
    for sent in id2sent:
        if keyword in sent.lower():
            if entity:
                # if ent2id[entity] not in sent2ent[sent2id[sent]]:
                if entity not in sent:
                    continue
                ret_str += hightlight(sent, keyword, entity=entity)
            else:
                print("highlighting")
                ret_str += hightlight(sent, keyword)

    return ret_str

def hightlight(sent, keyword, entity=None):
    a_template = "<FONT style=\"BACKGROUND-COLOR: yellow\"> {0} </FONT>"
    b_template = "<FONT style=\"BACKGROUND-COLOR: red\"> {0} </FONT>"
    c_template = "<FONT style=\"BACKGROUND-COLOR: #ABEBC6 \"> {0} </FONT>"
    raw_str = "<p>"

    # related entities
    ents = []
    if entity:
        # pdb.set_trace()
        ents = [e for e in sent2ent[sent2id[sent]]]
        ents = set(ents)
        if entity in ents:
            ents.remove(entity)

    #pdb.set_trace()
    if keyword != "":
        keyword_index = sent.lower().index(keyword.lower())
        tmp = sent[:keyword_index] + b_template.format(keyword) + sent[keyword_index + len(keyword):]
        sent = tmp
    
    if entity:
        ent_index = sent.index(entity)
        tmp = sent[:ent_index] + a_template.format(entity) + sent[ent_index + len(entity):]
        sent = tmp

        for ent in ents:
            try:
                ent_index = sent.index(ent)
                tmp = sent[:ent_index] + c_template.format(ent) + sent[ent_index + len(ent):]
                sent = tmp
            except:
                continue
    
    raw_str += sent
            
    raw_str += "</p>"
    return raw_str



search_icon.on_change('button_type', update_ner)
ner_select.on_change('value', update_ner)

# inital
update_ner(None, None, None)

l = layout([row(column(text, ner_select, search_icon), column(cand_text))])
curdoc().add_root(l)
curdoc().title = "Search Tool for Detecting Entities and Events"
