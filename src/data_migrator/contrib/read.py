#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import csv
import sys

from data_migrator.exceptions import DefinitionException
from data_migrator.exceptions import NonUniqueDataException
from data_migrator.utils import isstr


def read_map_from_csv(key=0, value=1, f=None, delimiter="\t", header=True,
                      as_list=False, unique=False):
    '''Generates a map from a csv and adds some validation and list parsing. A
    function that returns a map for MappingField to use as input in its
    MappingField.data_map.

        >>> from data_migrator.contrib.read import read_map_from_csv
        >>> table_map = read_map_from_csv(f=open('table.csv'), delimiter=';',
                                          key='id', value='name')
        >>> len(table_map)
        10

    Note that by default it is expected to have headers in the csv.

    Args:
        f: Filehandle to read the csv from into the map
        delimiter: Option to select another delimiter, other than `\\\\t`
        key: Name or position of the Key, if ``header`` is false, the ordinal
            position is expected (default first)
        value: Name or position of the Value, if ``header`` is false, the
            ordinal position is expected (default second)
        as_list (boolean): If ``True``, *data-migrator* will treat add all
            values for ``key`` as a list. Default is ``False``.
        unique (boolean): If ``True``, *data-migrator* will treat add all non
            unique values for ``key`` as a violation and raise a
            :exc:`~.NonUniqueDataException`. Default is ``False``.
        header (boolean): If ``True``, *data-migrator* will treat row as a
            header column. Default is ``True``

    Returns:
        map: a key, value map from the csv

    Raises:
        :exc:`~.DefinitionException`: if key, value does not match or as_list
            not set.
        :exc:`~.NonUniqueDataException`: if data is not unique on the key.

    '''
    data_map = {}
    if not f:
        f = sys.stdin
    r = csv.reader(f, delimiter=delimiter)

    if header:
        h = next(r, None)

    try:
        if isstr(key):
            ki = h.index(key)
        elif not header:
            ki = key
        else:
            raise DefinitionException('key=%s - should be string' % key)
        if isstr(value):
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
                raise NonUniqueDataException(
                    'line %d - unique constraint failed: %s' % (i, l[ki]))
            elif as_list:
                data_map[l[ki]] += v
            else:
                raise DefinitionException('line %d - unique contraint failed, expecting as_list for %s:%s' % (i, l[ki], data_map[l[ki]]))
        else:
            data_map[l[ki]] = v
    if f != sys.stdin:
        f.close()

    return data_map
