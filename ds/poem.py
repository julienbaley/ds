import regex as re
from itertools import chain, product

from .helpers import window, window_combinations
from .pronunciation import get_rhyme


class Poem(dict):
    def get_rhymes(self, lines=None, split=False):
        # this needs improvement: not every character will be a rhyme
        patt = r'，。）\]'
        end = '' if split else '$'

        return [last_char
                for line in (lines or self['paragraphs'])
                # add $ to force end of line
                for last_char in re.findall(f'([^{patt}])[{patt}]+{end}', line)
                ]

    def get_rhyme_categories(self):
        # retrieve characters that are in rhyme position
        rhymes = self.get_rhymes()

        # obtain their GY rhyme: many will have several possibilities
        # e.g. 長 => 陽 / 漾 / 養
        rhyme_sets = list(map(frozenset,
                              map(lambda rh: get_rhyme(rh, self['prons']),
                                  rhymes)))

        # disambiguate by looking at which rhymes would actually rhyme
        # e.g. if the line before/after contains 章 (陽 as the only possible
        # rhyme), then 長 must be read as the 陽 rhyme too.
        gy_rhymes = list()
        window_size = 5  # look 2 lines before and after

        for w in window(rhyme_sets, window_size, pad=True):
            candidate = w.pop(window_size//2)
            surrounding = set(chain.from_iterable(w))
            if len(candidate) > 1 and len(candidate & surrounding) > 0:
                # reduce to the set of possibilities (usu. down to 1)
                gy_rhymes.append(frozenset(candidate & surrounding))
            else:
                gy_rhymes.append(candidate)

        return [''.join(sorted(gy)) for gy in gy_rhymes]

    def find_rhyme_pairs(self, pair):
        gy_rhymes = self.get_rhyme_categories()
        rhyme_pairs = set(map(tuple, map(sorted,
                                         window_combinations(gy_rhymes, 2))))
        searched_pairs = set(map(tuple, map(sorted, product(*pair))))
        return set(searched_pairs) & set(rhyme_pairs)
