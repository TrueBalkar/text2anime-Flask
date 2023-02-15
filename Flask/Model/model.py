import pandas as pd
import numpy as np
from laserembeddings import Laser
import string
import copy
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import warnings
warnings.simplefilter(action='ignore')


def initialise_df():
    df = pd.read_json("Model/Clean_anime_general.json")
    desc = pd.read_json("Model/Description.json")
    char_desc = pd.read_json("Model/Character Description.json")
    reviews = pd.read_json("Model/Reviews embed.json").fillna(0)
    shiet = pd.read_json("Model/Processsed text.json", typ='series')

    return df, desc, char_desc, reviews, shiet


def get_general(char_desc, reviews, desc):
    char_desc_general = char_desc.mean()
    reviews_general = reviews.mean()
    desc_general = desc.mean()

    return char_desc_general, reviews_general, desc_general


def initialise_laser():
    path_to_bpe_codes = "Model/Laser_embd_down/93langs.fcodes"
    path_to_bpe_vocab = "Model/Laser_embd_down/93langs.fvocab"
    path_to_encoder = "Model/Laser_embd_down/bilstm.93langs.2018-12-26.pt"
    laser = Laser(path_to_bpe_codes, path_to_bpe_vocab, path_to_encoder)

    return laser


def embed_sentence(laser, sentence):
    return laser.embed_sentences(sentence, lang="en").reshape(1024)


def get_stop_words():
    return stopwords.words('english')


def search_similiar_items(query, stop, shiet, char_desc_general, reviews_general, desc_general, df, laser, char_desc,
                          reviews, desc, word_importance, context_importance, weights, auto_weight, filters):
    # Weight:
    # 1: Char description
    # 2: Reviews
    # 3: Description
    word_importance = float(word_importance)
    context_importance = float(context_importance)
    word_importance /= word_importance + context_importance
    context_importance /= word_importance + context_importance

    if filters:
        for item in filters:
            index_to_drop = df.index.where(df["Genres"].str.find(item) > -1).dropna()
            df = df.drop(index_to_drop, axis='index')
            shiet = shiet.drop(index_to_drop, axis='index')
            char_desc = char_desc.drop(index_to_drop, axis='index')
            reviews = reviews.drop(index_to_drop, axis='index')
            desc = desc.drop(index_to_drop, axis='index')

    ps = PorterStemmer()
    query_show = copy.copy(query)
    query = embed_sentence(laser, query)
    data = pd.DataFrame([query], index=["string"]).T
    data["item"] = np.NaN

    if auto_weight:
        buffer_w = pd.Series(index=['char_desc', 'reviews', 'desc'])
        data["item"] = char_desc_general
        buffer_w['char_desc'] = data.corr()["item"]["string"]
        data["item"] = reviews_general
        buffer_w['reviews'] = data.corr()["item"]["string"]
        data["item"] = desc_general
        buffer_w['desc'] = data.corr()["item"]["string"]

        suma = buffer_w["char_desc"] + buffer_w["reviews"] + buffer_w["desc"]
        weights[0] = (buffer_w["char_desc"] / suma) * 100
        weights[1] = (buffer_w["reviews"] / suma) * 100
        weights[2] = (buffer_w["desc"] / suma) * 100

    query_preprocess = word_tokenize(pd.Series(query_show).\
                                     apply(lambda x: ' '.join([word for word in x.split() if word not in stop])).\
                                     str.replace('[{}]'.format(string.punctuation), '')[0])
    stemmed = []
    for w in query_preprocess:
        stemmed.append(ps.stem(w))
    query_preprocess = copy.copy(stemmed)

    new_feature = pd.Series(0, index=df.index)
    for word in query_preprocess:
        new_feature += (shiet.str.find(word) > -1).astype("int64")

    new_feature /= new_feature.max()
    new_feature *= word_importance

    test = desc * weights[0] + char_desc * weights[1] + reviews * weights[2]

    buff = pd.Series(index=reviews.index)
    yield len(reviews)
    current = 1
    for index, item in zip(test.index, test.values):
        yield current
        data["item"] = item
        buff[index] = data.corr()["item"]["string"]
        current += 1
    buff *= context_importance
    buff += new_feature
    yield 'STOP'
    yield buff.nlargest(150)
