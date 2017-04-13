import csv
import sys

from data_migrator.exceptions import DataException, DefinitionException

def read_map_from_csv(key=0, value=1, f=sys.stdin, delimiter="\t", header=True, as_list=False, unique=False):
    '''Generates a map from csv'''
    data_map = {}

    r = csv.reader(f, delimiter=delimiter)

    if header:
        h = next(r, None)
    try:
        if isinstance(key, basestring):
            ki = h.index(key)
        elif not header:
            ki = key
        else:
            raise DefinitionException('key=%s - should be string' % key)
        if isinstance(value, basestring):
            vi = h.index(value)
        elif not header:
            vi = value
        else:
            raise DefinitionException("value=%s - should be string" % value)
    except ValueError as err:
        raise DefinitionException(err)
    i = 0
    for l in r:
        i += 1
        v = [l[vi]] if as_list else l[vi]
        if l[ki] in data_map:
            if unique:
                raise DataException('line %d - unique constraint failed: %s' % (i, l[ki]))
            elif as_list:
                data_map[l[ki]] += v
            else:
                raise DefinitionException('line %d - unqiue contraint failed, expecting as_list for %s:%s' % (i, l[ki], data_map[l[ki]]))
        else:
            data_map[l[ki]] = v
    if f != sys.stdin:
        f.close()

    return data_map
