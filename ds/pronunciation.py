import csv
import re
from collections import defaultdict
from functools import lru_cache
from itertools import filterfalse, zip_longest
from time import sleep

import requests
from bs4 import BeautifulSoup

CACHE_FILE = 'cache/pronunciation.cache.csv'
EDOC_URL = 'http://edoc.uchicago.edu/edoc2013/digitaledoc_linearformat.php'
EDOC_FIELDS = (('qygy[]', 'QYRhymeName'),
               ('qygy[]', 'GYRhymeName'),
               ('qygy[]', 'Shengdiao'),
               ('qygy[]', 'Baxter_GY'),
               ('qygy[]', 'fanqie'),
               ('qygy[]', 'Deng'),
               ('qygy[]', 'Kai_he'),
               ('qygy[]', 'ChineseName'),
               ('qygy[]', 'PingSheng'),
               ('qygy[]', 'SBGY'),
               ('bs2012[]', 'MCI'),
               ('bs2012[]', 'MCF'),
               ('bs2012[]', 'MCT'),
               ('bs2012[]', 'MC'),
               ('edoc[]', 'QY_IPA'),
               )
MAX_CHARS = 200


def query_edoc(chars):
    def get_html(chars):
        url_dic = [('text_input', chars),
                   ('Run_button', 'Display Phonetics'),
                   *EDOC_FIELDS,
                   ]

        return requests.post(EDOC_URL, data=url_dic).text

    def parse_result(html_string):
        ret = []
        soup = BeautifulSoup(html_string, 'html.parser')
        table = soup.findAll('table')[2]
        tr = table.find('tr')
        keys = tr.findAll('td')
        for tr in table.findAll('tr')[1:]:
            dic = dict()
            position = 0
            for td in tr.findAll('td'):
                dic[keys[position].text] = td.text
                position += 1
            dic.pop('')
            ret.append(dic)
        for i, entry in enumerate(ret):
            if len(entry['Graph']) == 0:
                ret[i]['Graph'] = ret[i-1]['Graph']
        return ret

    chunks = [list(filter(None, chunk))
              for chunk in zip_longest(*([iter(chars)] * MAX_CHARS))]

    ret = list()
    for i, chunk in enumerate(chunks, start=1):
        print(f'Chunk {i}/{len(chunks)}')
        ret.extend(parse_result(get_html((''.join(chunk)))))
        if i != 1:
            sleep(1)

    return ret


def get_and_cache_pronunciation(chars):
    ret = query_edoc(chars)

    cache = load_cache()
    for line in ret:
        cache[line['Graph']].append(line)
    dump_cache(cache, fields=list(line.keys()))


def dump_cache(cache, fields):
    with open(CACHE_FILE, 'w', newline='') as g:
        writer = csv.DictWriter(g, fieldnames=fields)
        writer.writeheader()
        for char in cache.values():
            for line in char:
                writer.writerow(line)
    load_cache.cache_clear()


@lru_cache()
def load_cache():
    ret = defaultdict(list)
    try:
        with open(CACHE_FILE) as f:
            reader = csv.DictReader(f)
            for line in reader:
                ret[line['Graph']].append(line)
    except FileNotFoundError:
        pass
    return ret

# tout ce qui est au-dessus est "privé"


def get_pronunciation(chars=None):
    cache = load_cache()
    if chars is None:
        return dict(cache)

    missing = list(filterfalse(cache.__contains__, set(chars)))

    if missing:
        print(f'Missing {len(missing)}')
        get_and_cache_pronunciation(missing)

    cache = load_cache()

    return {c: cache[c] for c in set(chars)}  # why not always return cache?


def get_final(pron):
    def extract_final_mcf(mcf):
        if mcf:
            mcf = re.sub('[+]', 'ɨ', mcf)
            return mcf

    def extract_final_baxter(bax):
        if bax:
            bax = re.sub('^y', 'j', bax)
            bax = re.sub('æ', 'ae', bax)
            return '-' + re.search('[aæeɛiɨjouw][^ HX]*', bax).group(0)

    def extract_final_schuessler(sch):
        if sch:
            sch = re.sub('jwo(?=[kŋ])', 'jow', sch)
            sch = re.sub('jwo', 'jo', sch)
            sch = re.sub('juən', 'jun', sch)
            sch = re.sub('uən', 'won', sch)
            sch = re.sub('uo', 'u', sch)
            sch = re.sub('ɐ(?=[kŋ])', 'æ', sch)
            sch = re.sub('ŋ', 'ng', sch)
            sch = re.sub('âu', 'aw', sch)
            sch = re.sub('juən', 'jun', sch)
            sch = re.sub('uậi', 'woj', sch)
            sch = re.sub('jɛt', 'it', sch)  # ?
            sch = re.sub('ä(?=[nt])', 'e', sch)
            sch = re.sub('jä', 'jie', sch)
            sch = re.sub('ăn', 'ean', sch)
            sch = re.sub('â', 'a', sch)
            sch = re.sub('ə', 'o', sch)
            sch = re.sub('̣', '', sch)
            try:
                return '-' + re.search('[aæeijouw][^ᶜᴮ ,]*', sch).group(0)
            except AttributeError:
                print(sch, pron)
                raise

    return [(extract_final_mcf(subpron['MCF']) or
             extract_final_baxter(subpron['GY Baxter']))
            for subpron in pron
            ] or [extract_final_schuessler(pron[0]['MC/QY'])]
