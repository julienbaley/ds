def filter_constraint(constraint_dict, it):
    for k, f in constraint_dict.items():
        it = filter(lambda a: f(a[k]), it)
    return list(it)
