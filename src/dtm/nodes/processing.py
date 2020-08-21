import re
import numpy as np
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from spacy.lang.en import English
from nltk.corpus import wordnet as wn

import spacy
from collections import OrderedDict
from spacy import displacy
from typing import List
import en_core_web_sm
nlp = en_core_web_sm.load()

nltk.download("wordnet")
nltk.download("stopwords")


def extract_entities(cleaned_data):
    cleaned_data_copy = cleaned_data.reset_index(drop=True).copy()
    lista_organisations = []
    for i in range(len(cleaned_data)):
        lista_org = org_entities(cleaned_data.iloc[i]["funding"]) or None
        lista_organisations.append(lista_org)
    cleaned_data_copy["org"] = lista_organisations
    return cleaned_data_copy


def clean_lower(data, var_list):

    for var in var_list:
        raw_corpora = data[(data[var].notnull()) & (data["type"]=="Research Paper")].copy()
        
        raw_corpora[var] = raw_corpora[var].fillna(" ")
        # No hyphens
        raw_corpora[var] = raw_corpora[var].map(lambda x: re.sub("—", "", x))
        raw_corpora[var] = raw_corpora[var].map(lambda x: re.sub("-", "", x))

        # Substitute punctuation with space
        raw_corpora[var] = raw_corpora[var].map(lambda x: re.sub("[.]", "", x))
        raw_corpora[var] = raw_corpora[var].map(lambda x: re.sub("[,!?]", " ", x))

        # Remove punctuation
        raw_corpora[var] = raw_corpora[var].map(
            lambda x: re.sub("[^a-zA-Z0-9]+", " ", x)
        )

        # Convert the titles to lowercase
        raw_corpora[var] = raw_corpora[var].map(lambda x: x.lower())

    return raw_corpora


def tokenize(text):
    parser = English()
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append("URL")
        elif token.orth_.startswith("@"):
            lda_tokens.append("SCREEN_NAME")
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)


def prepare_text_for_lda(text, stop_words):
    en_stop = set(nltk.corpus.stopwords.words("english"))

    en_stop.update(stop_words)
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 2]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    tokens = [get_lemma2(token) for token in tokens]
    return tokens


def extract_time_slices(df, time_var):
    time_intervals, time_slices = np.unique(df[time_var], return_counts=True)
    return time_intervals, time_slices


def create_processed(cleaned_data, var, time_var, stop_words):
    cleaned_data = cleaned_data[cleaned_data[var] != ""]
    time_intervals, time_slices = extract_time_slices(cleaned_data, time_var)
    cleaned_data[var] = cleaned_data[var].astype(str)

    processed_docs = cleaned_data[var].apply(
        prepare_text_for_lda, stop_words=stop_words
    )
    print("length    ", len(processed_docs))

    return time_intervals, time_slices, processed_docs


def org_entities(data: str) -> List[str]:
    entities = nlp(data).ents
    orgs = filter(lambda e: e.label_ == 'ORG', entities)
    orgs = map(lambda o: o.text, orgs)
    return list(dict.fromkeys(orgs))

