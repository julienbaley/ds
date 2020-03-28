from itertools import chain, combinations


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
