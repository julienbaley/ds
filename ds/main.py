import argparse
import pickle
import random
import re
from collections import Counter
from copy import deepcopy
from itertools import chain, compress, starmap
from multiprocessing.pool import Pool
from operator import attrgetter, itemgetter, mul
from os import cpu_count
from pprint import pprint
from time import time

import matplotlib.pyplot as plt
import pandas as pd
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
from gensim.corpora.dictionary import Dictionary
from gensim.matutils import corpus2csc
from gensim.models import CoherenceModel, Phrases
from gensim.models.ldamodel import LdaModel
from gensim.models.phrases import Phraser
from gensim.models.wrappers import LdaMallet
from gensim.models.wrappers.ldamallet import malletmodel2ldamodel
from sklearn.cluster import KMeans

from ds.authors import (NORTH, SOUTH, cache_authors, filter_by_area,
                        filter_by_time_range, keep_only_unambiguous,
                        load_authors)
from ds.community import (align_communities, get_community_rhyme_categories,
                          get_top_missing)
from ds.corpus import CORPORA, filter_by_authors, get_corpus
from ds.graph import (build_graph, get_communities, get_community_graph,
                      keep_only_communities, plot)
from ds.helpers import filter_constraint, takewhile_cdf
from ds.pronunciation import get_pronunciation, get_rhyme
from ds.replacements import replacements
from ds.sbgy import load_sbgy


def build(corpus):
    ret = dict()
    prons = get_pronunciation()
    ret['poems'] = corpus
    ret['graph'] = build_graph(ret['poems'])
    try:
        ret['communities'] = get_communities(ret['graph'])
    except:
        print(len(corpus))
        print(ret['graph'])
        raise
    ret['rhyme_groups'] = list(map(get_community_rhyme_categories,
                                   ret['communities']))
    return ret


def filter_poem_with_rime(rhyme_pair, corpus):
    return filter(lambda poem: poem.find_rhyme_pairs(rhyme_pair), corpus)


#def main():
if True:
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', choices=CORPORA.keys(), nargs='+')
    args = parser.parse_args()

    # Load authors and corpus
    all_authors = list()
    authors = dict()
    corpus = list()
    all_chars = set()
    for coll in args.collection:
        # cache_authors(coll)
        unambiguous = keep_only_unambiguous(load_authors(coll))
        authors[coll.upper()] = unambiguous
        all_authors.extend(unambiguous)
        corpus.extend(get_corpus(coll))
        all_chars |= set(
            chain.from_iterable(chain.from_iterable(poem['paragraphs']
                                                    for poem in corpus)))

    prons = get_pronunciation(chars=all_chars | set(replacements.values()))
    sbgy = load_sbgy()
    for poem in corpus:
        poem['prons'] = prons
        poem['sbgy'] = sbgy

    # Set various segmentations of the corpus
    authors.update({
        'FULL': all_authors,
        })

    corpora = {k: filter_by_authors(authors[k], corpus) for k in authors}
    corpora['all'] = corpus

    # Build!
    try:
        with open('/tmp/cache', 'rb') as f:
            results = pickle.load(f, encoding='utf-8')
    except FileNotFoundError:
        results = {k: build(corpora[k]) for k in corpora.keys()}
        with open('/tmp/cache', 'wb') as g:
            pickle.dump(results, g)

    communities = {k: [get_community_rhyme_categories(comm)
                       for comm in results[k]['communities']]
                   for k in corpora.keys()}

    poems = corpora['all']
