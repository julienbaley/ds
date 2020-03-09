import json
from glob import glob
from operator import itemgetter

from .helpers import filter_constraint
from .poem import Poem

CORPORA = {'qts': 'third-party/chinese-poetry/json/poet.tang',
           'qss': 'third-party/chinese-poetry/json/poet.song',
           'qsc': 'third-party/chinese-poetry/ci2/ci.song',
           }


def get_corpus(name):
    def clean_line(line):
        return line.replace('[', '').replace(']', '')

    def get_poems(filename):
        with open(filename) as f:
            js = json.load(f)
            for poem in js:
                poem['paragraphs'] = [clean_line(p)
                                      for p in poem['paragraphs']
                                      if p and not p.startswith('（')]
            return js

    ret = list()
    files = glob(f'{CORPORA[name]}.*[0-9].json')
    for filename in sorted(files, key=lambda fn: int(fn.split('.')[-2])):
        ret.extend(get_poems(filename))

    print(f'{len(ret)} poems in corpus')
    return list(map(Poem, ret))


def filter_by_authors(authors, corpus):
    if type(authors) != str:
        if all(issubclass(type(auth), dict) for auth in authors):
            authors = set(map(itemgetter('c_name_chn'), authors))

    else:
        return filter_by_authors({authors}, corpus)

    return filter_constraint({'author': authors.__contains__}, corpus)
