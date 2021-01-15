from collections import Counter
from operator import attrgetter, itemgetter

from .helpers import get_average_precision, takewhile_counter_cdf


def get_community_rhyme_categories(community):
    rhyme_cnt = Counter(rhyme for node in community for rhyme in node.rime)
    return Counter(dict(rhyme_cnt.most_common(8)))


def get_community_label(community, cdf=0.75):
    rhyme_cnt = Counter(rhyme for node in community for rhyme in node.rime)
    labels = takewhile_counter_cdf(rhyme_cnt, cdf=cdf)
    if '?' in labels:
        labels = labels[:labels.index('?')]
    return '/'.join(labels)


def align_communities(comms_a, comms_b):
    def top_rhymes(community, n):
        return list(map(itemgetter(0), community.most_common(n)))

    def basic_align(comms_1, comms_2):
        res = dict()
        for i, comm_1 in enumerate(comms_1):
            if len(comm_1) == 0:
                continue
            max_sc = 0
            max_j = -1
            for j, comm_2 in enumerate(comms_2):
                if len(comm_2) == 0:
                    continue
                mc = 3
                sc = get_average_precision(top_rhymes(comm_2, mc),
                                           top_rhymes(comm_1, mc))
                if sc > max_sc:
                    max_sc = sc
                    max_j = j
            if max_j != -1:
                res[i] = max_j
        return res

    def get_symmetric_score(comm_a, comm_b):
        mc = 8
        a_rhymes = top_rhymes(comm_a, mc)
        b_rhymes = top_rhymes(comm_b, mc)
        return max(get_average_precision(a_rhymes, b_rhymes),
                   get_average_precision(b_rhymes, a_rhymes))

    def overlap(comm_a, comm_b):
        return len(set(comm_a) & set(comm_b))

    # try aligning in both directions
    ab_align = basic_align(comms_a, comms_b)
    ba_align = basic_align(comms_b, comms_a)
    realign = dict()
    for k, v in ab_align.items():
        # where they don't agree, pick the highest one
        if ba_align[v] != k:
            ab = get_symmetric_score(comms_a[k], comms_b[v])
            ba = get_symmetric_score(comms_a[ba_align[v]], comms_b[v])
            overlap_ab = overlap(comms_a[k], comms_b[v])
            overlap_ba = overlap(comms_a[ba_align[v]], comms_b[v])

            if ba > ab or (ba == ab and overlap_ba > overlap_ab):
                k = ba_align[v]
        realign[k] = v

    ret = list()
    for k, v in realign.items():
        ret.append((comms_a[k], comms_b[v]))
    return ret


def get_top_missing(comm_a, comm_b):
    chars_in_common = set(comm_a) & set(comm_b)
    sorted_chars_a = list(map(itemgetter(0), comm_a.most_common()))
    useful_range = max(map(sorted_chars_a.index, chars_in_common))
    useful_chars = set(sorted_chars_a[:useful_range])
    return useful_chars - set(comm_b)


def community_node_to_set(community):
    return set(map(attrgetter('char'), community))
