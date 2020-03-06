import csv
import json
import re
from collections import Counter, defaultdict
from itertools import chain
from operator import itemgetter
from pprint import pprint

from tqdm import tqdm

from .cbdb import get_person


AUTHORS = {'qts': 'third-party/chinese-poetry/json/authors.tang.json',
           'qss': 'third-party/chinese-poetry/json/authors.song.json',
           }
DYNASTY = {'qts': '唐',
           'qss': '宋',
           'qsc': '宋',
           }
AUTHOR_CACHE = 'cache/authors.csv'


def get_authors(collection):
    with open(AUTHORS[collection]) as f:
        return json.load(f)


def get_zis(author):
    ret = set()
    for m in re.findall('字([^，。]{,6}?)[，。]', author['desc']):
        if '一作' in m:
            ret.add(re.sub('.一作', '', m))
            ret.add(re.sub('一作.', '', m))
        else:
            ret.add(m)
    for m in re.findall('諡曰([^，。]{,6}?)[，。]', author['desc']):
        ret.add(m)
    return ret


def write_cache(persons):
    with open(AUTHOR_CACHE, 'w', newline='') as g:
        writer = csv.DictWriter(g, fieldnames=persons[0].keys())
        writer.writeheader()
        for person in persons:
            writer.writerow(person)


def cache_authors(collection):
    authors = get_authors(collection)
    persons = [get_person(author['name'],
                          zis=get_zis(author),
                          dyn=DYNASTY.get(collection),
                          job='poet',
                          )
               for author in tqdm(authors)]

    pprint(Counter(map(len, persons)))
    persons = list(chain.from_iterable(persons))
    write_cache(persons)


def load_authors(collection):
    ret = defaultdict(list)
    with open(AUTHOR_CACHE) as f:
        reader = csv.DictReader(f)
        for line in reader:
            if line['dynasty'] == DYNASTY.get(collection):
                ret[line['c_name_chn']].append(line)

    print(f'{len(ret)} authors')
    return ret


def keep_only_unambiguous(authors):
    ret = list(map(itemgetter(0),
                   map(itemgetter(1),
                       filter(lambda ak_av: len(ak_av[1]) == 1,
                              authors.items()))))

    print(f'{len(ret)} authors left after ambiguous removed')
    return ret
