#!/usr/bin/python
# -*- coding: UTF-8 -*-

def sql_escape(v):
    '''Translate Python native types to SQL relevant strings'''
    if v is None:
        return "NULL"
    elif isinstance(v, basestring):
        return '"%s"' % v.replace('"', '""')
    else:
        return '%s' % v
