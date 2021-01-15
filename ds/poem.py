import regex as re
from collections import Counter
from itertools import chain, product
from operator import itemgetter

from .community import community_node_to_set
from .helpers import window, window_combinations
from .pronunciation import apply_tongyong, get_rhyme


class Poem(dict):
    def get_rhymes(self, lines=None, split=False):
        # this needs improvement: not every character will be a rhyme
        patt = r'，。？）\]」'
        end = '' if split else '$'

        return [last_char
                for line in (lines or self['paragraphs'])
                # add $ to force end of line
                for last_char in re.findall(f'([^{patt}])[{patt}]+{end}', line)
                ]

    def get_rhyme_categories(self, apply_eq=False):
        # retrieve characters that are in rhyme position
        rhymes = self.get_rhymes()

        # obtain their GY rhyme: many will have several possibilities
        # e.g. 長 => 陽 / 漾 / 養
        rhyme_gen = map(lambda rh: get_rhyme(rh, self['prons']), rhymes)
        if apply_eq:
            rhyme_gen = map(lambda cats:
                            map(lambda cat: apply_tongyong(cat, self['sbgy']),
                                cats),
                            rhyme_gen)
        rhyme_sets = list(map(frozenset, rhyme_gen))

        # disambiguate by looking at which rhymes would actually rhyme
        # e.g. if the line before/after contains 章 (陽 as the only possible
        # rhyme), then 長 must be read as the 陽 rhyme too.
        gy_rhymes = list()
        window_size = 3  # look 2 lines before and after

        for w in window(rhyme_sets, window_size, pad=True):
            candidate = w.pop(window_size//2)
            surrounding = set(chain.from_iterable(w))
            if len(candidate) > 1 and len(candidate & surrounding) > 0:
                # reduce to the set of possibilities (usu. down to 1)
                gy_rhymes.append(frozenset(candidate & surrounding))
            else:
                gy_rhymes.append(candidate)

        return [''.join(sorted(gy)) or '?' for gy in gy_rhymes]

    def get_rhyme_communities(self, communities):
        community_sets = list(map(community_node_to_set, communities))
        ret = list()
        community_candidates = [
            [i for i, comm in enumerate(community_sets) if rhyme in comm]
            for rhyme in self.get_rhymes()
            ]
        counts = Counter(chain.from_iterable(community_candidates))
        for candidates in community_candidates:
            if len(candidates) == 1:
                ret.append(candidates[0])
            else:
                for comm in map(itemgetter(0), counts.most_common()):
                    if comm in candidates:
                        ret.append(comm)
                        break
                else:
                    ret.append('?')

        return ret

    def groups_to_annotations(self, groups):
        ret = list()
        next_letter = 'a'
        annotations = dict()
        for para, group in zip(self['paragraphs'], groups):
            if group not in annotations:
                annotations[group] = next_letter
                next_letter = chr(ord(next_letter) + 1)
            ret.append(annotations[group])
        return ret

    def annotate(self, annotations):
        ret = list()

        for para, rhyme, rime_group in zip(self['paragraphs'],
                                           self.get_rhymes(),
                                           annotations):
            idx = para.rindex(rhyme)
            ret.append(para[:idx] + f'[{rime_group}]' + para[idx:])

        return ret

    def get_naive_annotations(self):
        return self.groups_to_annotations(map(lambda _: 'a',  # any constant
                                              self.get_rhymes()))

    def get_category_annotations(self, apply_tongyong=False):
        return self.groups_to_annotations(
            self.get_rhyme_categories(apply_tongyong))

    def get_community_annotations(self, communities):
        return self.groups_to_annotations(
            self.get_rhyme_communities(communities))

    def annotate_on_category(self, apply_tongyong=False):
        return self.annotate(self.get_category_annotations(apply_tongyong))

    def annotate_on_community(self, communities):
        return self.annotate(self.get_community_annotations(communities))

    def find_rhyme_pairs(self, pair):
        gy_rhymes = self.get_rhyme_categories()
        rhyme_pairs = set(map(tuple, map(sorted,
                                         window_combinations(gy_rhymes, 2))))
        searched_pairs = set(map(tuple, map(sorted, product(*pair))))
        return set(searched_pairs) & set(rhyme_pairs)
