import ast
import json
from collections import Counter
from itertools import combinations
from operator import itemgetter

ANNOTATED = 'gold/rhyme_judgment.json'
CORPORA = 'gold/corpus.json'


def get_annotated_poems():
    try:
        with open(ANNOTATED) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_annotated_poems(poems):
    with open(ANNOTATED, 'w') as g:
        json.dump(poems, g, ensure_ascii=False, indent=4)


def annotate_poem(results, poem):
    print('\n\n')
    print(poem.annotate_on_category(True))
    print(poem.annotate_on_community(results['northerners']['communities']))
    print(list(map(lambda c: '/'.join(map(itemgetter('GY Baxter'),
                                          poem['prons'][c])),
                   poem.get_rhymes())))
    print(poem.get_rhyme_categories())
    return ast.literal_eval(input())


def annotate_poems(results, poems):
    annotated_poems = get_annotated_poems()
    for i, poem in enumerate(poems, start=1):
        print(i)
        annotation = annotate_poem(results, poem)
        annotated_poems[poem['id']] = annotation
        save_annotated_poems(annotated_poems)


def get_corpora():
    try:
        with open(CORPORA) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_corpora(corpora):
    with open(CORPORA, 'w') as g:
        json.dump(corpora, g, ensure_ascii=False, indent=4)


def get_non_annotated_corpora():
    corpora = get_corpora()
    annotated_poems = get_annotated_poems()
    ret = list()
    for corpus in corpora:
        ret.append({'name': corpus['name'],
                    'description': corpus['description'],
                    'ids': [id
                            for id in corpus['ids']
                            if id not in annotated_poems]})
    return ret


def add_corpus(ids, name, description):
    corpora = get_corpora()
    corpus = {'name': name,
              'description': description,
              'ids': ids}
    corpora.append(corpus)
    save_corpora(corpora)


def find_poems(results, ids):
    return [poem
            for poem in results['all']['poems']
            if poem['id'] in set(ids)]


def get_non_annotated_poems(results):
    corpora = get_non_annotated_corpora()
    ret = list()
    for corpus in corpora:
        ret.append({'name': corpus['name'],
                    'description': corpus['description'],
                    'poems': find_poems(results, corpus['ids'])})
    return ret


def score_annotator(results, annotated_poems, annotator):
    cnt = Counter()
    for id, gold_annotated_poem in annotated_poems.items():
        poem = find_poems(results, {id, })[0]
        annotated_poem = annotator(poem)
        cnt[gold_annotated_poem == annotated_poem] += 1
    return cnt


def accuracy(pattern1, pattern2):
    def to_binary(pattern):
        return [a == b for a, b in combinations(pattern, 2)]

    t1 = to_binary(pattern1)
    t2 = to_binary(pattern2)
    return sum(a == b for a, b in zip(t1, t2)) / len(t1)
