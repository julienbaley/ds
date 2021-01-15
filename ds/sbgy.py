import re
from collections import namedtuple

from bs4 import BeautifulSoup

Rime = namedtuple('Rime', ['rime', 'tone', 'eq', 'duyong'], defaults=[''])
SBGY = 'third-party/sbgy/sbgy.xml'


def iter_volumes(soup):
    return soup.find_all('volume')


def get_tone(volume):
    return re.search('.(?=聲)', volume.find_next('volume_title').text).group()


def get_rhymes(soup):
    ret = dict()
    tongyong = dict()
    for volume in iter_volumes(soup):
        tone = get_tone(volume)
        for entry in volume.find_next('catalog').find_all('rhythmic_entry'):
            entry.find('fanqie').decompose()  # throw away the fanqie

            char = entry.text.strip()[0]

            note = entry.find('note')
            eqs = list()
            duyong = False
            if note is not None:
                note = note.extract().text  # duyong, tongyong
                if match := re.search('^.*(?=同用)', note):
                    eqs = list(match.group())
                duyong = note == '獨用'
            for c in eqs:
                tongyong[c] = char

            ret[char] = Rime(char, tone, tongyong.get(char), duyong)

    return ret


def load_sbgy():
    with open(SBGY) as f:
        soup = BeautifulSoup(f, 'html.parser')
        return get_rhymes(soup)
