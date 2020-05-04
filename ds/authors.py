import csv
import json
import re
from collections import Counter, defaultdict
from itertools import chain
from multiprocessing.pool import Pool
from operator import itemgetter
from os import cpu_count
from pprint import pprint

from tqdm import tqdm

from .cbdb import get_person
from .helpers import filter_constraint


AUTHORS = {'qts': 'third-party/chinese-poetry/json/authors.tang.json',
           'qss': 'third-party/chinese-poetry/json/authors.song.json',
           }
DYNASTY = {'qts': '唐',
           'qss': '宋',
           'qsc': '宋',
           }
AUTHOR_CACHE = 'cache/authors.{0}.csv'

NORTH = {'河南', '陝西', '河北', '山西', '山東', '甘肅', '北京', '遼寧', '天津',
         '新疆', '寧夏', '内蒙古'}
SOUTH = {'江蘇', '浙江', '福建', '江西', '四川', '安徽', '湖北', '湖南', '廣東',
         '廣西', '上海', '雲南', '貴州', '海南'}


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


def write_cache(persons, collection):
    with open(AUTHOR_CACHE.format(collection), 'w', newline='') as g:
        writer = csv.DictWriter(g, fieldnames=persons[0].keys())
        writer.writeheader()
        for person in persons:
            writer.writerow(person)


def get_person_wrapper(kwargs):
    return get_person(**kwargs)


def cache_authors(collection):
    authors = get_authors(collection)
    kwargs = [dict(name=author['name'],
                   zis=get_zis(author),
                   dyn=DYNASTY.get(collection),
                   job='poet',
                   )
              for author in authors]

    with Pool(cpu_count()-1) as p:
        persons = [person
                   for person in tqdm(p.imap(get_person_wrapper, kwargs),
                                      total=len(kwargs))]

    pprint(Counter(map(len, persons)))
    persons = list(chain.from_iterable(persons))
    write_cache(persons, collection)


def load_authors(collection):
    ret = defaultdict(list)
    with open(AUTHOR_CACHE.format(collection)) as f:
        reader = csv.DictReader(f)
        for line in reader:
            line['c_index_year'] = (int(line['c_index_year'])
                                    if line['c_index_year']
                                    else None)
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


def filter_by_area(area, authors):
    if type(area) == str:
        return filter_by_area({area}, authors)

    return filter_constraint({'province': area.__contains__}, authors)


def filter_by_time_range(time_range, authors):
    return filter_constraint({'c_index_year': time_range.__contains__},
                             authors)
