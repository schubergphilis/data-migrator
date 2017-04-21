#!/usr/bin/python
# -*- coding: UTF-8 -*-
from data_migrator.utils.compat import isstr

def sql_escape(v):
    '''Translate Python native types to SQL relevant strings'''
    if v is None:
        return "NULL"
    elif isstr(v):
        return '"%s"' % v.replace('"', '""')
    else:
        return '%s' % v
