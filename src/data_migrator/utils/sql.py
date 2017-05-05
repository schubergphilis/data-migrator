#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json

from data_migrator.utils.compat import isstr

def sql_escape(v):
    '''Translate Python native types to SQL relevant escaped strings

        >>> sql_escape(None)
        'NULL'
        >>> sql_escape("hello")
        '"hello"'
        >>> sql_escape('["hello"]')
        '"[""hello""]"'
        >>> sql_escape('{"hello":"world"}')
        '"{""hello"":""world""}"'
        >>> sql_escape({"hello":"world"})
        '"{""hello"": ""world""}"'
        >>> sql_escape(0)
        '0'
        >>> sql_escape("0")
        '"0"'
        >>> sql_escape('0')
        '"0"'

    Args:
        v: value to Translate

    Returns:
        str: escaped string to be inserted in sql statement
    '''

    if v is None:
        return "NULL"
    elif isstr(v):
        return '"%s"' % v.replace('"', '""')
    elif isinstance(v, dict) or isinstance(v, list):
        return '"%s"' % json.dumps(v).replace('"', '""')
    else:
        return '%s' % v
