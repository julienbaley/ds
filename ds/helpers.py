from itertools import chain, combinations


def annotation_to_selectors(annotation_list):
    return [[annotation == k for annotation in annotation_list]
            for k in set(annotation_list)]


def filter_constraint(constraint_dict, it):
    for k, f in constraint_dict.items():
        it = filter(lambda a: f(a[k]), it)
    return list(it)


def window(lst, n, pad=False):
    if pad and len(lst) > 0:
        assert n % 2 == 1 and n > 1
        padding = [type(lst[0])()] * (n // 2)
        lst = padding + lst + padding
    return [lst[i:i+n] for i in range(len(lst)-(n-1))]


def window_combinations(lst, wsize):
    '''Slides a window over input and returns the combinations of items in each
    window; typical use cases are wsize=2 which is equivalent to listing the
    windows, and wsize=len(lst) which will give all the combinations of rhymes
    '''
    return set(chain.from_iterable(map(lambda w: list(combinations(w, 2)),
                                       window(lst, wsize))))


def get_precision_vector(results, truth):
    ret = list()
    relevant = 0
    for rank, result in enumerate(results, start=1):
        if result in truth:
            relevant += 1
        ret.append(relevant / rank)
    return ret


def get_average_precision(results, truth):
    precision_vector = get_precision_vector(results, truth)

    tot = 0
    for rank, relevant in enumerate(truth, start=0):
        if relevant in results:
            tot += precision_vector[results.index(relevant)]
    return tot / len(truth)


def takewhile_cdf(dict_lst, cdf=0.96):
    tot = sum(map(lambda x: sum(x.values()), dict_lst))
    cum = 0
    for x in sorted(dict_lst, key=lambda x: sum(x.values()), reverse=True):
        yield x
        cum += sum(x.values()) / tot
        if cum >= cdf:
            break


def get_counter_cdf(counter):
    tot = sum(counter.values())
    cum = 0
    ret = list()
    for k, v in counter.most_common():
        cum += v
        ret.append((k, cum/tot))
    return ret


def takewhile_counter_cdf(counter, cdf=0.75):
    ret = list()
    for k, v in get_counter_cdf(counter):
        ret.append(k)
        if v > cdf:
            break
    return ret
