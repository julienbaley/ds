import osr
import shapefile
from pyproj import CRS, Transformer
from shapely.geometry import shape, Point
from shapely.ops import transform

prov90 = 'third-party/gis/v6_citas90_prov_pgn_gbk'
pref90 = 'third-party/gis/v6_citas90_pref_pgn_gbk'


def get_transormer(prj_file):
    prj_text = open(prj_file, 'r').read()
    srs = osr.SpatialReference()
    if srs.ImportFromWkt(prj_text):
        raise ValueError("Error importing PRJ information from: %s" % prj_file)
    crs = CRS.from_proj4(srs.ExportToProj4())

    return Transformer.from_crs(crs, 4326)


def get_reader(db):
    params = dict()
    for ext in ['dbf', 'shp', 'shx', 'prj']:
        params[ext] = open(f"{db}.{ext}", "rb")
    encoding = db.split('_')[-1]

    return shapefile.Reader(**params, encoding=encoding)


transformer = get_transormer(f'{prov90}.prj')
readers = {'province': get_reader(prov90),
           'prefecture': get_reader(pref90),
           }

for k, v in readers.items():
    srs = readers[k].shapeRecords()
    readers[k].provinces = list()
    for province in srs:
        gi = province.shape.__geo_interface__
        province.sh = transform(transformer.transform, shape(gi))
        readers[k].provinces.append(province)


def get_first(dic, keys):
    for key in keys:
        if key in dic:
            return dic[key]
    raise KeyError(keys)


def get_province(*, y, x, type='province'):
    if not x:
        return None
    for province in readers[type].provinces:
        if Point(y, x).within(province.sh):
            d = province.record.as_dict()
            return get_first(d, ['NAME_HZ', 'NAME_FT', 'HZ_NAME'])
