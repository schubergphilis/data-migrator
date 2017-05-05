#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json

from data_migrator.utils.compat import isstr

def sql_escape(v):
    '''Translate Python native types to SQL relevant escaped strings'''
    if v is None:
        return "NULL"
    elif isstr(v):
        return '"%s"' % v.replace('"', '""')
    elif isinstance(v, dict) or isinstance(v, list):
        return '"%s"' % json.dumps(v).replace('"', '""')
    else:
        return '%s' % v
