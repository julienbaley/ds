import sqlite3
from contextlib import contextmanager
from itertools import groupby
from operator import itemgetter, methodcaller

from .gis import get_province

DB_FILE = 'third-party/cbdb/CBDB_20190424.db'
LIFE_SPAN = 80  # years
DYNASTIES = {'唐': range(618, 908),
             '宋': range(960, 1279),
             }


@contextmanager
def get_cursor():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    yield conn.cursor()


def rows2dicts(rows):
    return [dict(zip(row.keys(), row)) for row in rows]


def pick_one_per_address(res):
    return [next(addresses)
            for _, addresses in groupby(res, key=itemgetter('c_personid'))]


def merge(d):
    if len(d) != 2:
        return d

    ret = list()
    for xs in zip(*map(sorted, map(methodcaller('items'), d))):
        kw = xs[0][0]
        vals = set(filter(None, map(itemgetter(1), xs)))
        if len(vals) == 1 or kw == 'c_personid':
            ret.append((kw, vals.pop()))
        elif len(vals) == 0:
            ret.append((kw, None))
        else:
            return d
    fewest_nones = min(d, key=lambda x: list(x.values()).count(None))
    ret.append(('c_personid', fewest_nones['c_personid']))
    return [dict(ret)]


def query_name(name):
    with get_cursor() as cursor:

        cursor.execute(
            f'''SELECT DISTINCT
                    biog_main.c_personid, biog_main.c_name_chn,
                    c_index_year, c_birthyear, c_deathyear, c_dynasty_chn,
                    addresses.c_name_chn as address, x_coord, y_coord

                FROM biog_main
                LEFT JOIN biog_addr_data
                ON biog_main.c_personid == biog_addr_data.c_personid
                LEFT JOIN addresses
                ON biog_addr_data.c_addr_id == addresses.c_addr_id
                LEFT JOIN dynasties
                ON biog_main.c_dy == dynasties.c_dy

                WHERE biog_main.c_name_chn == "{name}"
                ''')

        return cursor.fetchall()


def filter_by_alternative_name(rows, zis):
    '''Takes a list of rows of people (sharing the same name) and a list of
    alternative name (zi, hao, hao etc) and returns a filtered list based on
    the alternative names. If the result is an empty list, returns the original
    rows instead'''

    ids = tuple(map(itemgetter('c_personid'), rows))
    with get_cursor() as cursor:
        cursor.execute(
            f'''SELECT DISTINCT
                    c_personid
                FROM altname_data
                WHERE c_personid IN {ids}
                AND c_alt_name_chn IN ("{'","'.join(zis)}")
                ''')
        filtered_ids = set(map(itemgetter('c_personid'), cursor.fetchall()))

    if len(filtered_ids) != 0:
        return list(filter(lambda row: row['c_personid'] in filtered_ids,
                           rows))
    else:
        return rows


def filter_by_job(rows, job):
    ids = tuple(map(itemgetter('c_personid'), rows))
    with get_cursor() as cursor:
        cursor.execute(
            f'''SELECT status_data.c_personid
                FROM status_data
                JOIN status_codes
                ON status_codes.c_status_code == status_data.c_status_code
                WHERE c_personid IN {ids}
                AND c_status_desc == '{job}';
            ''')
        filtered_ids = list(map(itemgetter('c_personid'), cursor.fetchall()))

    if len(filtered_ids) != 0:
        return list(filter(lambda row: row['c_personid'] in filtered_ids,
                           rows))
    else:
        return rows


def filter_by_period(dicts, time_range):
    def matches(dic):
        start = dic['c_birthyear'] or None
        end = dic['c_deathyear'] or None
        idx = dic['c_index_year'] or None
        if start is None and end is None and idx is None:
            return True  # this is arbitrary, could be false too...
        else:
            if start is None:
                if end is None:  # idx cannot be None
                    start = idx - LIFE_SPAN
                    end = idx + LIFE_SPAN
                else:
                    start = end - LIFE_SPAN
            if end is None:
                end = start + LIFE_SPAN
        return bool(set(range(start, end+1)) & set(time_range))

    if time_range is not None:
        return list(filter(matches, dicts))
    else:
        return dicts


# only public method

def get_person(name, zis=None, dyn=None, job=None):
    rows = query_name(name)

    if len(rows) > 1 and zis:
        rows = filter_by_alternative_name(rows, zis)

    if len(rows) > 1 and job:
        rows = filter_by_job(rows, job)

    dicts = rows2dicts(rows)
    dicts = pick_one_per_address(dicts)
    dicts = filter_by_period(dicts, DYNASTIES.get(dyn))

    for p in dicts:
        p['dynasty'] = p.pop('c_dynasty_chn') or dyn
        p['province'] = get_province(x=p['x_coord'], y=p['y_coord'])
        p['prefecture'] = get_province(x=p['x_coord'], y=p['y_coord'],
                                       type='prefecture')

    return merge(dicts)  # I am not sure anymore what this is for
